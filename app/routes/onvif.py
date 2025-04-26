from onvif import ONVIFCamera

class ONVIF(ONVIFCamera):
    """
    :param host: IP-адрес камеры.
    :param port: Порт ONVIF.
    :param user: Логин для доступа к камере.
    :param passwd: Пароль для доступа к камере.
    """

    def __init__(
        self,
        host,
        port,
        user,
        passwd,
        **kwargs,
    ):

        super().__init__(host, port, user, passwd, **kwargs)

    def activate(self):
        self.ptz = self.create_ptz_service()
        self.media = self.create_media_service()
        self.profile_token = self.media.GetProfiles()[0].token
        return self
