from github_automation.common.constants import OR


def get_first_column_items(client, config):
    response = client.get_first_column_items(owner=config.project_owner,
                                             name=config.repository_name,
                                             project_number=config.project_number,
                                             is_org_project=config.is_org_project)
    project = get_project_from_response(response, config.is_org_project)
    project_cards = get_project_cards(project)
    cards_page_info = project_cards.get('pageInfo', {})
    while cards_page_info.get('hasNextPage'):
        new_response = client.get_first_column_items(owner=config.project_owner,
                                                     name=config.repository_name,
                                                     project_number=config.project_number,
                                                     start_cards_cursor=cards_page_info['endCursor'],
                                                     is_org_project=config.is_org_project)
        project = get_project_from_response(new_response, config.is_org_project)
        new_cards = get_project_cards(project)
        project_cards['edges'].extend(new_cards['edges'])
        cards_page_info = new_cards['pageInfo']

    return response


def get_column_items_with_prev_column(client, config, prev_cursor):
    response = client.get_column_items(owner=config.project_owner,
                                       name=config.repository_name,
                                       project_number=config.project_number,
                                       prev_column_id=prev_cursor,
                                       is_org_project=config.is_org_project)
    project = get_project_from_response(response, config.is_org_project)
    project_cards = get_project_cards(project)
    cards_page_info = project_cards.get('pageInfo', {})
    while cards_page_info.get('hasNextPage'):
        new_response = client.get_column_items(owner=config.project_owner,
                                               name=config.repository_name,
                                               project_number=config.project_number,
                                               prev_column_id=prev_cursor,
                                               start_cards_cursor=cards_page_info['endCursor'],
                                               is_org_project=config.is_org_project)
        project = get_project_from_response(new_response, config.is_org_project)
        new_cards = get_project_cards(project)
        project_cards['edges'].extend(new_cards['edges'])
        cards_page_info = new_cards['pageInfo']

    return response


def is_matching_project_item(item_labels, must_have_labels, cant_have_labels, filter_labels):
    if not any([(value in item_labels) for value in filter_labels]):
        return False

    for label in must_have_labels:
        if OR in label:
            new_labels = label.split(OR)
            if all(new_label not in item_labels for new_label in new_labels):
                return False

        elif label not in item_labels:
            return False

    for label in cant_have_labels:
        if label in item_labels:
            return False

    return True


def get_labels(label_edges):
    label_names = []
    for edge in label_edges:
        node_data = edge.get('node')
        if node_data:
            label_names.append(node_data['name'])

    return label_names


def get_project_from_response(response, is_org_project):
    root = response['organization'] if is_org_project else response['repository']
    return root.get('project', {})


def get_project_cards(project):
    if project:
        if 'columns' in project:
            columns = project['columns']
            if 'nodes' in columns and isinstance(columns['nodes'], list):
                nodes = columns['nodes']
                if len(nodes) > 0 and 'cards' in nodes[0]:
                    return nodes[0]['cards']
    return {}
