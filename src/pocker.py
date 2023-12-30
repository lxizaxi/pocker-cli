import re
from datetime import datetime, timezone

import docker  # type: ignore
import typer
from rich import box
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

app = typer.Typer()


def get_docker_client():
    return docker.from_env()


def format_age(created):
    created = re.sub(r"\.\d+Z$", "Z", created)
    created_datetime = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )
    now = datetime.now(timezone.utc)
    delta = now - created_datetime

    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    created_content: str = ""  # type: ignore
    if not days == 0:
        created_content += f"{days}d "
    if not hours == 0:
        created_content += f"{hours}h "
    if not minutes == 0:
        created_content += f"{minutes}m "
    created_content += "just now" if created_content == "" else "ago"

    return created_content


def format_size(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    size_in_bytes = int(size)
    for unit in units:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024


def format_ports(ports_dict):
    formatted_ports: list[str] = []  # type: ignore
    for container_port in ports_dict:
        port_dict = ports_dict[container_port][0]

        host_ip = port_dict["HostIp"]
        host_port = port_dict["HostPort"]

        formatted_ports.append(f"{host_ip}:{host_port} -> {container_port}")

    return ", ".join(formatted_ports)


def docker_ps_format(container, color="white"):
    return [
        f"[{color}]{container.short_id}[/]",
        f"[{color}]{container.image.tags[0] if container.image.tags else ''}[/]",
        f"[{color}]{container.attrs['Config']['Cmd']}[/]",
        f"[{color}]{format_age(container.attrs['Created'])}[/]",
        f"[{color}]{container.status}[/]",
        f"[{color}]{format_ports(container.attrs['HostConfig']['PortBindings'])}[/]",
        f"[{color}]{container.name}[/]",
    ]


def docker_images_format(image, color="white"):
    repository, tag = image.tags[0].split(":") if image.tags else ("", "")
    return [
        f"[{color}]{repository}[/]",
        f"[{color}]{tag}[/]",
        f"[{color}]{image.short_id.split(':')[-1]}[/]",
        f"[{color}]{format_age(image.attrs['Created'])}[/]",
        f"[{color}]{format_size(image.attrs['Size'])}[/]",
    ]


@app.command("ps")
def docker_ps(
    all: Annotated[
        bool,
        typer.Option(
            "-a",
            "--all",
            help="Show all containers, including stopped ones (-a option).",
        ),
    ] = False,
):
    containers = get_docker_client().containers.list(all=all)

    table = Table(box=box.ROUNDED)
    table.add_column("CONTAINER ID")
    table.add_column("IMAGE")
    table.add_column("COMMAND")
    table.add_column("CREATED")
    table.add_column("STATUS")
    table.add_column("PORTS")
    table.add_column("NAMES")

    for container in containers:
        color = "green" if container.status == "running" else "red"
        table.add_row(*docker_ps_format(container, color=color))

    Console().print(table)


@app.command("images")
def docker_images(
    all: Annotated[
        bool,
        typer.Option(
            "-a",
            "--all",
            help="Show all images, including intermediate images (-a option).",
        ),
    ] = False,
):
    images = get_docker_client().images.list(all=all)

    table = Table(box=box.ROUNDED)
    table.add_column("REPOSITORY")
    table.add_column("TAG")
    table.add_column("IMAGE ID")
    table.add_column("CREATED")
    table.add_column("SIZE")

    for image in images:
        color = "green"  # ToDo: danglingイメージを赤にしたい
        table.add_row(*docker_images_format(image, color=color))

    Console().print(table)


def main():
    app()


if __name__ == "__main__":
    main()
