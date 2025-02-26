import logging

import feedparser
import requests

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


VIDAL_BASE_URL = "https://api.vidal.fr"


class VidalApi(models.Model):
    _name = "vidal.api"
    _description = "Vidal Service"

    def get_authentication(self):
        company = self.env.company
        authentication = (
            "?app_id="
            + company.vidal_client_id
            + "&app_key="
            + company.vidal_client_secret
        )
        return authentication

    def api_post(self, url, data, full=False):
        headers = {"Content-Type": "text/xml"}
        authentication = self.get_authentication()
        url_request = (
            VIDAL_BASE_URL + ("/rest/api/" if not full else "") + url + authentication
        )
        try:
            r = requests.post(url_request, data=data, headers=headers, timeout=20)
            if r.status_code == 500:
                raise UserError(
                    _(
                        "Erreur vidal Internal Server Error 500 sur %s : \
                        Contactez INVITU !"
                    )
                    % (url_request)
                )
            elif r.status_code not in [200, 201]:
                raise UserError(
                    _(
                        "Message vidal %(message)s - Detail %(detail)s - \
                        Error %(code)s sur %(url)s : \
                        Contactez INVITU !"
                    )
                    % {
                        "message": r.json().get("message"),
                        "detail": r.json().get("detail"),
                        "code": r.status_code,
                        "url": url_request,
                    }
                )
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            _logger.exception(e)
            raise UserError(
                _(
                    "We had trouble to create your data, please retry later or\
                    contact your support if the problem persists - Network \
                    Error sur %s"
                )
                % (url_request)
            ) from e
        return feedparser.parse(r.content)

    def api_get(self, url, full=False, **kwargs):
        authentication = self.get_authentication()
        url_request = (
            VIDAL_BASE_URL
            + ("/rest/api/" if not full else "")
            + url
            + authentication
            + "&"
            + "&".join(f"{k}={v}" for k, v in kwargs.items())
        )
        try:
            r = requests.get(url_request, timeout=20)
            if r.status_code == 500:
                raise UserError(
                    _(
                        "Erreur vidal Internal Server Error 500 sur %s : \
                        Contactez INVITU !"
                    )
                    % (url_request)
                )
            elif r.status_code != 200:
                raise UserError(
                    _(
                        "Message vidal %(message)s - Detail %(detail)s - \
                        Error %(code)s sur %(url)s : \
                        Contactez INVITU !"
                    )
                    % {
                        "message": r.json().get("message"),
                        "detail": r.json().get("detail"),
                        "code": r.status_code,
                        "url": url_request,
                    }
                ) from None
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            _logger.exception(e)
            raise UserError(
                _(
                    "We had trouble to create your data, please retry later or\
                    contact your support if the problem persists - Network \
                    Error sur %s"
                )
                % (url_request)
            ) from e
        return feedparser.parse(r.content)
