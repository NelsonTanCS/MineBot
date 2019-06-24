# `MineBot`
> A small Discord bot for the Discord Hack Week.

![][tag-image]
![][tag2-image]

Someone suggested that my [`minesweeper`](https://github.com/LeptoSpira/minesweeper) Discord cog I created should be published as a bot for the Discord Hack Week. So I did just that, Turned it into a simple bot and here it is!

![Header Image][header-image.png]

## Features
- Usage of my [`minesweeper`](https://github.com/LeptoSpira/minesweeper) cog
- Snazzy [32x32 Minesweepers][example-output]

## Setup
### Dependencies
- `discord.py`
- `numpy`

### Installation
```bash
pip(version) install -r requirements.txt
python(version) minebot.py
```

## Usage
1. Create an application and discord bot at https://discordapp.com/developers/applications/
1. Create a `config.json` file with:

    ```
    {
      "token": "your-discord-bot-token",
    }
    ```


## Footnote
LeptoSpira - Discord: `@LeptoSpira#4548`

Distributed under the MIT license. See `LICENSE` for more information.

**[https://github.com/LeptoSpira/MineBot](https://github.com/LeptoSpira/)**

<!-- Markdown link & img dfn's -->
[tag-image]: https://img.shields.io/github/license/LeptoSpira/MineBot.svg
[tag2-image]: https://img.shields.io/badge/Hypesquad-Brilliance-ea7a66.svg
[header-image.png]: https://i.imgur.com/3slzIe4.png
[example-output]: https://camo.githubusercontent.com/2701c6ebe637823fb85841d2f6ce49eaccb38d15/68747470733a2f2f63646e2e646973636f72646170702e636f6d2f6174746163686d656e74732f3436313932363839303331323330323539342f3538323733303938333037343239393930342f756e6b6e6f776e2e706e67
