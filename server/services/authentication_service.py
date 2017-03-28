from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from server.models.dtos.user_dto import AuthorizedDTO
from server.models.postgis.user import User


class AuthServiceError(Exception):
    """ Custom Exception to notify callers an error occurred when authenticating """
    def __init__(self, message):
        if current_app:
            current_app.logger.error(message)


class AuthenticationService:

    def login_user(self, osm_user_details, user_element='user'):

        osm_user = osm_user_details.find(user_element)

        if osm_user is None:
            raise AuthServiceError('User element not found in OSM response')

        osm_id = int(osm_user.attrib['id'])
        username = osm_user.attrib['display_name']
        existing_user = User().get(osm_id)

        if not existing_user:
            changesets = osm_user.find('changesets')
            changeset_count = int(changesets.attrib['count'])

            User.create_from_osm_user_details(osm_id, username, changeset_count)

        auth_dto = AuthorizedDTO()
        auth_dto.username = username
        auth_dto.session_token = self._generate_session_token_for_user(osm_id)

        return auth_dto

    def _generate_session_token_for_user(self, osm_id: int):
        """
        Generates a unique token with the osm_id and current time embedded within it
        :param osm_id: OSM ID of the user authenticating
        :return: Token
        """
        serializer = URLSafeTimedSerializer(current_app.secret_key)

        # Generate token using email
        token = serializer.dumps(osm_id)
        return token
