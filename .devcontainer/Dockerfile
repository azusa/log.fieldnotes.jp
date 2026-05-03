FROM node:22-bookworm-slim

ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=1000

RUN userdel -r node 2>/dev/null || true

RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    fonts-noto-cjk \
    build-essential \
    curl \
    dnsutils \
    git \
    htop \
    iproute2 \
    iputils-ping \
    jq \
    less \
    lsof \
    netcat-openbsd \
    procps \
    python3 \
    python3-pip \
    rsync \
    strace \
    sudo \
    tmux \
    tree \
    unzip \
    vim \
    zip \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i 's/# ja_JP.UTF-8/ja_JP.UTF-8/' /etc/locale.gen && locale-gen
ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8

RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} \
    && usermod -aG sudo ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

RUN mkdir -p /home/${USERNAME}/.npm && chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.npm

USER dev
WORKDIR /workspace
