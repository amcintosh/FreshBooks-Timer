from fbtimer import FRESHBOOKS_BASE_URL
from fbtimer.service.auth import auth


def get_business(token):
    res = auth(token).get(
        '{}{}'.format(
            FRESHBOOKS_BASE_URL,
            'auth/api/v1/users/me'
        )).json()['response']
    business_list = []
    for index, business_membership in enumerate(res['business_memberships'], start=1):
        business = business_membership['business']
        business_list.append(
            (business['name'], business['id'], business['account_id'])
        )
        print('{}. {}'.format(index, business['name']))
    selected = input('Which business would you like to sign into: ')
    return business_list[int(selected) - 1]
