#!/usr/bin/python3

import subprocess, json, urllib.request, os
import logging, argparse, tarfile, time

rootLogger = logging.getLogger('deploy')



def create_images_dir(args):
    rootLogger.info("Start make images directory")
    try:
        if not os.path.exists(args.imagesPath):
            os.makedirs(args.imagesPath)
            rootLogger.info("Images directory created")
            return True
        else:
            rootLogger.info("Images directory already exists")
            return False
    except Exception as ex:
        rootLogger.error("Create images directory failed {}".format(ex))
        exit(1)


def download_images(args):
    rootLogger.info("Start download images")
    try:
        urllib.request.urlretrieve(args.imagesUrl, os.path.join(args.imagesPath, 'pandapics.tar.gz'))
        rootLogger.info("Images archive downloaded")
    except Exception as ex:
        rootLogger.error("Can't download images archive {}".format(ex))
        exit(1)

def open_images_archive(args):
    rootLogger.info("Start open archive")
    try:
        tar = tarfile.open(os.path.join(args.imagesPath, 'pandapics.tar.gz'))
        tar.extractall(args.imagesPath)
        rootLogger.info("Open archive success")
    except Exception as ex:
        rootLogger.error("Can't open images archive {}".format(ex))
        exit(1)


def start_docker_compose_app():
    rootLogger.info("Start run docker-compose")
    cmd = "docker-compose up -d"
    try:
        subprocess.run(cmd, shell=True)
        rootLogger.info("Run docker-compose success")
    except Exception as ex:
        rootLogger.error("Run docker-compose failed {}".format(ex))
        exit(1)

def print_compose_information():
    cmd = "docker-compose ps"
    try:
        output = subprocess.check_output(cmd, shell=True)
        rootLogger.info("Print docker-compose success")
        print(output)
    except Exception as ex:
        rootLogger.error("Print docker-compose failed {}".format(ex))
        exit(1)

def healthcheck(args):
    rootLogger.info("Start Healthcheck")
    try:
        response = urllib.request.urlopen(args.appHealthcheck);
        result = json.load(response)
        print(result)
    except Exception as ex:
        rootLogger.error("Health check failed {}".format(ex))
        exit(1)


def make_logger(args):
    global rootLogger
    log_level_name = getattr(logging, args.logLevel.upper())
    rootLogger.setLevel(log_level_name)
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    fileHandler = logging.FileHandler(args.logfile)
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(log_level_name)
    rootLogger.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(log_level_name)
    rootLogger.addHandler(consoleHandler)



def make_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--imagesUrl', action="store", default="https://s3.eu-central-1.amazonaws.com/devops-exercise/pandapics.tar.gz", help="Download images URL")
    parser.add_argument('--logfile', action="store", default="./deploy.log", help="Change log file path")
    parser.add_argument('--logLevel', action="store", default="INFO", help="Set log level")
    parser.add_argument('--imagesPath', action="store", default="./images", help="Directory for store images")
    parser.add_argument('--appHealthcheck', action="store", default="http://localhost:3000/health", help="Application healthcheck url")

    return parser.parse_args()


def main():
    args = make_args()
    make_logger(args)
    rootLogger.info("Start Run")
    if create_images_dir(args):
        download_images(args)
    open_images_archive(args)
    start_docker_compose_app()
    print_compose_information()
    healthcheck(args)



if __name__ == "__main__":
    main()
