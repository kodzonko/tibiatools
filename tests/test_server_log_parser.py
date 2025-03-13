def test_parser_reads_actions_correctly():
    from tibiatools.server_log_parser import parse_server_log

    df = parse_server_log(
        r"C:\Users\janwa\AppData\Local\Tibia\packages\Tibia\log\Server Log.txt"
    )
    print(df.head())
    print(df.tail())
