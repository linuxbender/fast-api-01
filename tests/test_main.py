"""Unit tests for app.__main__ module."""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestMainModule:
    """Test __main__ module entry point."""

    def test_import_main_module(self):
        """Test that __main__ module can be imported."""
        import app.__main__ as main_module

        assert hasattr(main_module, "main")
        assert callable(main_module.main)

    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        from app.__main__ import main

        assert callable(main)


class TestMainArguments:
    """Test command line argument parsing."""

    def test_main_with_default_arguments(self):
        """Test main function with default arguments (no args)."""
        with patch("app.__main__.uvicorn.run") as mock_uvicorn:
            with patch("app.__main__.get_settings") as mock_settings:
                with patch("app.__main__.has_ssl_certificates", return_value=True):
                    mock_settings.return_value = Mock(
                        server_host="127.0.0.1",
                        server_port=8000,
                        server_reload=True,
                        environment="development",
                        ssl_keyfile="certs/private.key",
                        ssl_certfile="certs/certificate.crt",
                    )
                    sys.argv = ["app"]

                    from app.__main__ import main

                    main()

                    mock_uvicorn.assert_called_once()

    def test_main_with_host_argument(self):
        """Test main function with --host argument."""
        with patch("app.__main__.uvicorn.run") as mock_uvicorn:
            with patch("app.__main__.get_settings") as mock_settings:
                with patch("app.__main__.has_ssl_certificates", return_value=True):
                    mock_settings.return_value = Mock(
                        server_host="127.0.0.1",
                        server_port=8000,
                        server_reload=True,
                        environment="development",
                        ssl_keyfile="certs/private.key",
                        ssl_certfile="certs/certificate.crt",
                    )
                    sys.argv = ["app", "--host", "0.0.0.0"]

                    from app.__main__ import main

                    main()

                    call_args = mock_uvicorn.call_args
                    assert call_args[1]["host"] == "0.0.0.0"

    def test_main_with_port_argument(self):
        """Test main function with --port argument."""
        with patch("app.__main__.uvicorn.run") as mock_uvicorn:
            with patch("app.__main__.get_settings") as mock_settings:
                with patch("app.__main__.has_ssl_certificates", return_value=True):
                    mock_settings.return_value = Mock(
                        server_host="127.0.0.1",
                        server_port=8000,
                        server_reload=True,
                        environment="development",
                        ssl_keyfile="certs/private.key",
                        ssl_certfile="certs/certificate.crt",
                    )
                    sys.argv = ["app", "--port", "9000"]

                    from app.__main__ import main

                    main()

                    call_args = mock_uvicorn.call_args
                    assert call_args[1]["port"] == 9000

    def test_main_with_no_reload_argument(self):
        """Test main function with --no-reload argument."""
        with patch("app.__main__.uvicorn.run") as mock_uvicorn:
            with patch("app.__main__.get_settings") as mock_settings:
                with patch("app.__main__.has_ssl_certificates", return_value=True):
                    mock_settings.return_value = Mock(
                        server_host="127.0.0.1",
                        server_port=8000,
                        server_reload=True,
                        environment="development",
                        ssl_keyfile="certs/private.key",
                        ssl_certfile="certs/certificate.crt",
                    )
                    sys.argv = ["app", "--no-reload"]

                    from app.__main__ import main

                    main()

                    call_args = mock_uvicorn.call_args
                    assert call_args[1]["reload"] is False

    def test_main_with_workers_argument(self):
        """Test main function with --workers argument."""
        with patch("app.__main__.uvicorn.run") as mock_uvicorn:
            with patch("app.__main__.get_settings") as mock_settings:
                with patch("app.__main__.has_ssl_certificates", return_value=True):
                    mock_settings.return_value = Mock(
                        server_host="127.0.0.1",
                        server_port=8000,
                        server_reload=True,
                        environment="development",
                        ssl_keyfile="certs/private.key",
                        ssl_certfile="certs/certificate.crt",
                    )
                    sys.argv = ["app", "--workers", "4"]

                    from app.__main__ import main

                    main()

                    call_args = mock_uvicorn.call_args
                    assert call_args[1]["workers"] == 4


class TestSSLCertificateGeneration:
    """Test SSL certificate generation in main."""

    def test_main_generates_certificates_if_missing(self):
        """Test that main generates SSL certificates if they don't exist."""
        with patch("app.__main__.uvicorn.run"):
            with patch("app.__main__.get_settings") as mock_settings:
                with patch(
                    "app.__main__.has_ssl_certificates", return_value=False
                ):
                    with patch(
                        "app.__main__.SSLCertificateGenerator"
                    ) as mock_gen_class:
                        mock_gen_instance = MagicMock()
                        mock_gen_class.return_value = mock_gen_instance

                        mock_settings.return_value = Mock(
                            server_host="127.0.0.1",
                            server_port=8000,
                            server_reload=True,
                            environment="development",
                            ssl_keyfile="certs/private.key",
                            ssl_certfile="certs/certificate.crt",
                        )
                        sys.argv = ["app"]

                        from app.__main__ import main

                        main()

                        # Verify SSLCertificateGenerator was instantiated
                        mock_gen_class.assert_called_once()
                        # Verify create_certificate_directory was called
                        mock_gen_instance.create_certificate_directory.assert_called_once()
                        # Verify generate was called
                        mock_gen_instance.generate.assert_called_once_with(days_valid=365)

    def test_main_uses_existing_certificates(self):
        """Test that main uses existing certificates if available."""
        with patch("app.__main__.uvicorn.run"):
            with patch("app.__main__.get_settings") as mock_settings:
                with patch(
                    "app.__main__.has_ssl_certificates", return_value=True
                ):
                    with patch(
                        "app.__main__.SSLCertificateGenerator"
                    ) as mock_gen_class:
                        mock_settings.return_value = Mock(
                            server_host="127.0.0.1",
                            server_port=8000,
                            server_reload=True,
                            environment="development",
                            ssl_keyfile="certs/private.key",
                            ssl_certfile="certs/certificate.crt",
                        )
                        sys.argv = ["app"]

                        from app.__main__ import main

                        main()

                        # SSLCertificateGenerator should NOT be called
                        mock_gen_class.assert_not_called()


class TestMainErrorHandling:
    """Test error handling in main."""

    def test_main_handles_keyboard_interrupt(self):
        """Test that main handles KeyboardInterrupt gracefully."""
        with patch("app.__main__.uvicorn.run") as mock_uvicorn:
            with patch("app.__main__.get_settings") as mock_settings:
                with patch("app.__main__.has_ssl_certificates", return_value=True):
                    mock_uvicorn.side_effect = KeyboardInterrupt()
                    mock_settings.return_value = Mock(
                        server_host="127.0.0.1",
                        server_port=8000,
                        server_reload=True,
                        environment="development",
                        ssl_keyfile="certs/private.key",
                        ssl_certfile="certs/certificate.crt",
                    )
                    sys.argv = ["app"]

                    from app.__main__ import main

                    # Should not raise, handles gracefully
                    main()

    def test_main_handles_server_error(self):
        """Test that main handles server errors gracefully."""
        with patch("app.__main__.uvicorn.run") as mock_uvicorn:
            with patch("app.__main__.get_settings") as mock_settings:
                with patch("app.__main__.has_ssl_certificates", return_value=True):
                    mock_uvicorn.side_effect = Exception("Server error")
                    mock_settings.return_value = Mock(
                        server_host="127.0.0.1",
                        server_port=8000,
                        server_reload=True,
                        environment="development",
                        ssl_keyfile="certs/private.key",
                        ssl_certfile="certs/certificate.crt",
                    )
                    sys.argv = ["app"]

                    from app.__main__ import main

                    with pytest.raises(SystemExit) as exc_info:
                        main()

                    assert exc_info.value.code == 1


class TestMainServerConfiguration:
    """Test server configuration in main."""

    def test_main_uses_settings_defaults(self):
        """Test that main respects default settings."""
        with patch("app.__main__.uvicorn.run") as mock_uvicorn:
            with patch("app.__main__.get_settings") as mock_settings:
                with patch("app.__main__.has_ssl_certificates", return_value=True):
                    mock_settings.return_value = Mock(
                        server_host="0.0.0.0",
                        server_port=9000,
                        server_reload=False,
                        environment="production",
                        ssl_keyfile="certs/key.pem",
                        ssl_certfile="certs/cert.pem",
                    )
                    sys.argv = ["app"]

                    from app.__main__ import main

                    main()

                    call_args = mock_uvicorn.call_args
                    assert call_args[1]["host"] == "0.0.0.0"
                    assert call_args[1]["port"] == 9000
                    assert call_args[1]["reload"] is False

    def test_main_command_line_args_override_settings(self):
        """Test that CLI args override settings defaults."""
        with patch("app.__main__.uvicorn.run") as mock_uvicorn:
            with patch("app.__main__.get_settings") as mock_settings:
                with patch("app.__main__.has_ssl_certificates", return_value=True):
                    mock_settings.return_value = Mock(
                        server_host="127.0.0.1",
                        server_port=8000,
                        server_reload=True,
                        environment="development",
                        ssl_keyfile="certs/private.key",
                        ssl_certfile="certs/certificate.crt",
                    )
                    sys.argv = ["app", "--host", "0.0.0.0", "--port", "9000"]

                    from app.__main__ import main

                    main()

                    call_args = mock_uvicorn.call_args
                    assert call_args[1]["host"] == "0.0.0.0"
                    assert call_args[1]["port"] == 9000

    def test_main_uses_ssl_settings(self):
        """Test that main uses SSL settings from configuration."""
        with patch("app.__main__.uvicorn.run") as mock_uvicorn:
            with patch("app.__main__.get_settings") as mock_settings:
                with patch("app.__main__.has_ssl_certificates", return_value=True):
                    mock_settings.return_value = Mock(
                        server_host="127.0.0.1",
                        server_port=8000,
                        server_reload=True,
                        environment="development",
                        ssl_keyfile="/path/to/key.pem",
                        ssl_certfile="/path/to/cert.pem",
                    )
                    sys.argv = ["app"]

                    from app.__main__ import main

                    main()

                    call_args = mock_uvicorn.call_args
                    assert call_args[1]["ssl_keyfile"] == "/path/to/key.pem"
                    assert call_args[1]["ssl_certfile"] == "/path/to/cert.pem"
