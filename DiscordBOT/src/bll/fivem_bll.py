import os

import requests
import socketio

from dotenv import load_dotenv


load_dotenv()


class FiveMBLL:

    @staticmethod
    def sync_player_job(discord_id, job, grade):

        txadmin_url = os.getenv("TXADMIN_URL")
        username = os.getenv("TXADMIN_USERNAME")
        password = os.getenv("TXADMIN_PASSWORD")

        # =========================
        # VALIDAR CONFIGURAÇÃO
        # =========================

        if not txadmin_url:
            return {
                "success": False,
                "status": "not_configured",
                "message": "TXADMIN_URL não configurado."
            }

        if not username:
            return {
                "success": False,
                "status": "not_configured",
                "message": "TXADMIN_USERNAME não configurado."
            }

        if not password:
            return {
                "success": False,
                "status": "not_configured",
                "message": "TXADMIN_PASSWORD não configurado."
            }

        # =========================
        # CONSTRUIR COMANDO
        # =========================

        command = (
            f"discordsetjob "
            f"{discord_id} "
            f"{job} "
            f"{int(grade)}"
        )

        session = requests.Session()

        try:

            # =========================
            # LOGIN NO TXADMIN
            # =========================

            login_response = session.post(
                f"{txadmin_url.rstrip('/')}/auth/password",
                json={
                    "username": username,
                    "password": password
                },
                timeout=10
            )

            login_response.raise_for_status()

            login_data = login_response.json()

            csrf_token = login_data.get("csrfToken")

            if not csrf_token:
                return {
                    "success": False,
                    "status": "login_error",
                    "message": "txAdmin não devolveu o CSRF token."
                }

            print(
                "[TXADMIN] Login efetuado com sucesso."
            )

            # =========================
            # CRIAR SOCKET.IO
            # =========================

            sio = socketio.Client(
                reconnection=False,
                logger=False,
                engineio_logger=False
            )

            command_sent = False

            # =========================
            # CONNECT
            # =========================

            @sio.event
            def connect():

                print(
                    "[TXADMIN] Socket.IO conectado."
                )

            # =========================
            # CONNECT ERROR
            # =========================

            @sio.event
            def connect_error(data):

                print(
                    f"[TXADMIN] Erro Socket.IO: {data}"
                )

            # =========================
            # DISCONNECT
            # =========================

            @sio.event
            def disconnect():

                print(
                    "[TXADMIN] Socket.IO desligado."
                )

            # =========================
            # CONSOLE DATA
            # =========================

            @sio.on("consoleData")
            def console_data(data):

                nonlocal command_sent

                print(
                    "[TXADMIN] consoleData recebido."
                )

                if command_sent:
                    return

                command_sent = True

                print(
                    f"[TXADMIN] A enviar: {command}"
                )

                sio.emit(
                    "consoleCommand",
                    command
                )

            # =========================
            # COOKIES
            # =========================

            cookies = "; ".join(
                f"{cookie.name}={cookie.value}"
                for cookie in session.cookies
            )

            # =========================
            # SOCKET.IO
            # =========================
            #
            # A sala liveconsole é enviada
            # através da query string.
            #
            # =========================

            socket_url = (
                f"{txadmin_url.rstrip('/')}"
                f"/?rooms=liveconsole"
            )

            sio.connect(
                socket_url,
                transports=["polling"],
                headers={
                    "Cookie": cookies,
                    "x-txadmin-csrftoken": csrf_token
                },
                socketio_path="/socket.io"
            )

            # =========================
            # ESPERAR EVENTOS
            # =========================

            sio.sleep(5)

            # =========================
            # DESLIGAR
            # =========================

            if sio.connected:
                sio.disconnect()

            # =========================
            # RESULTADO
            # =========================

            if command_sent:

                print(
                    f"[TXADMIN] Comando enviado: {command}"
                )

                return {
                    "success": True,
                    "status": "executed",
                    "message": command
                }

            print(
                "[TXADMIN] Não foi recebido consoleData."
            )

            return {
                "success": False,
                "status": "command_not_sent",
                "message": "txAdmin não enviou consoleData."
            }

        # =========================
        # ERROS REQUESTS
        # =========================

        except requests.RequestException as error:

            print(
                f"[TXADMIN] Erro HTTP: {error}"
            )

            return {
                "success": False,
                "status": "connection_error",
                "message": str(error)
            }

        # =========================
        # ERROS SOCKET.IO / OUTROS
        # =========================

        except Exception as error:

            print(
                f"[TXADMIN] Erro: {error}"
            )

            return {
                "success": False,
                "status": "error",
                "message": str(error)
            }