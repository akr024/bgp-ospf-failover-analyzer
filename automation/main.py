from getpass import getpass
from ssh_client import run_command

def main():
    host = "172.20.20.3"
    username = "root"
    command = "vtysh -c 'show ip ospf neighbor'"

    password = getpass("SSH Password: ")

    print(f"Connecting to {host}")

    output = run_command(host,username,password,command)

    print(output)

if __name__ == "__main__":
    main()
