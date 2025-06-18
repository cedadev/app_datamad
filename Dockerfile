#####
## Docker image for DataMad
#####

ARG BASE_IMAGES_REGISTRY=registry.ceda.ac.uk/base-images
ARG BASE_IMAGES_VERSION="latest"

ARG GIT_REPOSITORY=https://github.com/cedadev/app_datamad
# This should be set to a fixed commit of the code repository
# To rebuild with a newer version of the code, update this variable and commit
# This ensures that the build for any given commit to this build repository is repeatable
ARG GIT_VERSION=07a3f6596d15dc94d3e20fe610d69b4c40096aad

FROM ${BASE_IMAGES_REGISTRY}/git-checkout:${BASE_IMAGES_VERSION} AS application-source

FROM ${BASE_IMAGES_REGISTRY}/python-build:${BASE_IMAGES_VERSION} AS python-build

FROM ${BASE_IMAGES_REGISTRY}/django:${BASE_IMAGES_VERSION}

# Install packages needed for mysqlclient to run into the final deployment image
# Change user to root for package installation
USER root
RUN crb enable
RUN dnf install -y \
   python3-devel \
   mysql-server \
   pkgconf \
   pkgconf-pkg-config \
   mysql-devel \
   && dnf clean all

# Change user back to $WSGI_UID
USER $WSGI_UID
