from checks import run_checks


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true', help='Add / Subtract User Groups in Tableau Server')
    parser.add_argument('--test', action='store_true', help='Run checks on data sources')
    args = parser.parse_args()

    if args.run:
        print('Running job')
        from main import update_group_assigments
        update_group_assigments()

    if args.test:
        import checks
        checks.run_checks()