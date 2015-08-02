from engine import ContainerLoader
import sys

def main():
    loader = ContainerLoader()
    loader.main(sys.argv[1:])
