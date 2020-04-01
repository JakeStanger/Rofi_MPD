import os.path

import appdirs
import toml


def load_default():
    return dict(
        music_directory='~/Music',
        case_sensitive=False,
        enable_disc_names=True,
        tracks_keep_open=True,
        discs_keep_open=True,
        play_on_add=False,
        hosts=[
            dict(
                host='localhost',
                port=6600
            )
        ]
    )


def load_config():
    config_dir = appdirs.user_config_dir('rofi-mpd', 'Jake Stanger')
    config_path = os.path.join(config_dir, 'config.toml')

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = toml.loads(f.read())
    else:
        config = load_default()

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        with open(config_path, 'w') as f:
            toml.dump(config, f)

    return config
