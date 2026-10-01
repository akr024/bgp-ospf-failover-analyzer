import paramiko

def run_command(
    host: str,
    username: str,
    password: str,
    command: str
) -> str:
    netDevice = paramiko.SSHClient()
    netDevice.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    try:
        netDevice.connect(hostname=host, username=username, password=password)

        stdin, stdout, stderr = netDevice.exec_command(command=command)

        output = stdout.read().decode('utf-8')

        error = stderr.read().decode('utf-8')

        exitStatus = stdout.channel.recv_exit_status()
        
        if(exitStatus != 0):
            raise RuntimeError(f"Command failed with exit status: {exitStatus} and error: {error}")

        return output

    finally:
        netDevice.close()
