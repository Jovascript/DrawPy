'''Main file for running a command file'''
import logging
import sys
import argparse

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Get JCode(drawing format) for an svg file.")
    parser.add_argument("-v", "--verbose", action="store_true")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--svg", help="An SVG file to draw")
    group.add_argument("-f", "--file", help="A raw command file to draw")
    group.add_argument("-w", "--web", help="Launch the web interface", action="store_true")

    args = parser.parse_args()
    # Check whether file is specified.
    if args.svg or args.file:
        from drawpi.svgreader import parse, slice
        from drawpi.runner import main, setup_logging
        # Setup the logger
        setup_logging(args.verbose)
        logger = logging.getLogger()
        if args.svg:
            with open(args.svg, 'r') as f:
                text = f.read()
            commands = slice(parse(text))
        else:
            with open(args.file, 'r') as f:
                commands = f.read()
        main(commands)
    elif args.web:
        # Server time
        import webserver
        webserver.app.run()

