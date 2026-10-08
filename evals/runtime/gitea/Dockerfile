FROM golang:1.25.5-bookworm@sha256:d9132cce84391efab786495288756d60e1da215b1f94e87860aeefc3d4c45b6d
ENV CGO_ENABLED=1 CGO_CFLAGS="-O2 -g -DSQLITE_MAX_VARIABLE_NUMBER=32766" GOTOOLCHAIN=local
WORKDIR /tmp/dependencies
COPY go.mod go.sum ./
RUN go mod download
RUN useradd --create-home --uid 1000 --shell /bin/bash codekick
USER codekick
ENV GOCACHE=/home/codekick/.cache/go-build GOPATH=/home/codekick/go
RUN go mod download
WORKDIR /workspace
