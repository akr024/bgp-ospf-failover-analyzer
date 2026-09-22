FROM quay.io/frrouting/frr:10.7.1

RUN apk add --no-cache openssh-server iputils && \
    mkdir -p /var/run/sshd && \
    echo 'root:frr123' | chpasswd && \
    sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    ssh-keygen -A
