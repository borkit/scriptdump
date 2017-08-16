import logging

import boto3


def copy_security_group_to_vpc(group, vpc):
    """Copies an EC2 security group to a new security group in a different VPC.

    Creates a new security group in vpc using settings on the existing
    group (name, description, ingress rules, egress rules, tags).

    Args:
        group: The (boto3) ec2.SecurityGroup to be copied.
        vpc: The destination ec2.Vpc.

    Returns:
        The newly created ec2.SecurityGroup.
    """

    from_slug = make_security_group_slug(group)
    to_slug = make_security_group_slug(vpc, group.group_name)

    logging.info('copying %s to %s', from_slug, to_slug)
    logging.info('description: %s', repr(group.description))
    logging.info('tags: %s', repr(group.tags))
    logging.info('ip_permissions: %s', repr(group.ip_permissions))
    logging.info('ip_permissions_egress: %s', repr(group.ip_permissions_egress))

    to_group = vpc.create_security_group(
            GroupName=group.group_name,
            Description=group.description
        )

    to_slug = make_security_group_slug(to_group)
    logging.info('created %s', repr(to_slug))

    if group.tags is not None:
        tags = to_group.create_tags(
                Tags=group.tags
            )
        logging.info('tags: %s', repr(tags))

    # revoke default rules and copy rules from source group
    for permissions, action in [
            (to_group.ip_permissions, 'revoke_ingress'),
            (to_group.ip_permissions_egress, 'revoke_egress'),
            (group.ip_permissions, 'authorize_ingress'),
            (group.ip_permissions_egress, 'authorize_egress'),
        ]:
        if len(permissions) > 0:
            method = getattr(to_group, action)
            response = method(IpPermissions=permissions)
            logging.info('response from %s: %s', action, repr(response))

    return to_group


def make_security_group_slug(group_or_vpc, group_name=None):
    parts = [get_region_name(group_or_vpc), group_or_vpc.vpc_id]
    if hasattr(group_or_vpc, 'group_id'):
        parts.append(group_or_vpc.group_id)
        group_name = group_or_vpc.group_name
    parts.append(group_name)
    return repr(tuple(parts))


def get_region_name(resource):
    return resource.meta.client.meta.region_name


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('group', help='Security group ID or name')
    # TODO support from/to account
    parser.add_argument('--from-region', help='Source region name')
    parser.add_argument('--from-vpc', help='Source VPC ID')
    parser.add_argument('--to-region', help='Destination region name')
    parser.add_argument('--to-vpc', help='Destination VPC ID')
    #parser.add_argument('--overwrite', help='Apply changes to destination group if it exists', action='store_true')
    args = parser.parse_args()

    from_ec2 = boto3.resource('ec2', region_name=args.from_region)

    group = find_security_group(from_ec2, args.group, args.from_vpc)

    if args.to_region is None:
        args.to_region = args.from_region
    if args.to_region == args.from_region:
        to_ec2 = from_ec2
    else:
        to_ec2 = boto3.resource('ec2', region_name=args.to_region)

    vpc = find_vpc(to_ec2, args.to_vpc)

    copy_security_group_to_vpc(group, vpc)


def find_security_group(ec2, group_id_or_name, vpc_id=None):
    if group_id_or_name.startswith('sg-'):
        filter_name = 'group-id'
    else:
        filter_name = 'group-name'
    filters = [make_filter(filter_name, group_id_or_name)]
    if vpc_id is not None:
        filters.append(make_filter('vpc-id', vpc_id))
    group = find_single_result(ec2, 'security_groups', filters, 'vpc_id')
    return group


def find_vpc(ec2, vpc_id=None):
    if vpc_id is None:
        name = 'isDefault'
        value = 'true'
    else:
        name = 'vpc-id'
        value = vpc_id
    filters = [make_filter(name, value)]
    vpc = find_single_result(ec2, 'vpcs', filters)
    return vpc


def find_single_result(ec2, collection_name, filters, *scope_names):
    region_name = get_region_name(ec2)
    collection = getattr(ec2, collection_name)
    search = collection.filter(Filters=filters)
    results = list(search)
    if len(results) > 1:
        msg = 'Too many matching ' + collection_name + ':'
        for result in results:
            msg += ' '
            scope_ids = [getattr(result, _) for _ in scope_names]
            msg += repr(tuple([region_name, *scope_ids, result.id]))
        raise ValueError(msg)
    if len(results) < 1:
        raise ValueError('No matching ' + collection_name)
    return results[0]


def make_filter(name, *values):
    return {'Name': name, 'Values': list(values)}


if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
