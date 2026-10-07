# Gameplay and Feature Guide

This guide explains what Alien Invasion does from a player's perspective. For
implementation details, see the [code guide](code-guide.md).

## Objective

The player controls Earth's defence ship at the bottom of the screen. Move left
or right, fire upward, and destroy every alien before the fleet collides with the
ship or reaches the atmosphere.

Clearing a fleet starts the next level. Each new fleet moves faster until the
selected difficulty's speed cap is reached.

## Starting a game

Select **Play** on the main menu to open Mission Select. Choose one game mode and
one difficulty, then select **Start**.

### Modes

| Mode | Goal | End condition |
| --- | --- | --- |
| Classic | Survive and clear as many fleets as possible | All ships are lost |
| Time Attack | Score as many points as possible in 2 minutes | Time expires or all ships are lost |

### Difficulties

| Difficulty | Starting ships | Fleet behavior | Score multiplier |
| --- | ---: | --- | ---: |
| Easy | 5 | Slower start and gentler acceleration | 0.8× |
| Normal | 3 | Balanced movement and acceleration | 1.0× |
| Hard | 2 | Faster start, larger drops, and quicker acceleration | 1.5× |

## Controls

| Action | Input |
| --- | --- |
| Move left | Left Arrow or `A` |
| Move right | Right Arrow or `D` |
| Fire | Press or hold Space |
| Pause or resume | Escape |
| Move menu focus | Arrow keys or Tab |
| Activate focused control | Enter or Space |

All menu controls can also be selected with the mouse.

## Weapons

The ship fires straight upward. Two rules limit firing:

1. A short cooldown must finish between shots.
2. No more than three bullets can be active simultaneously.

The ten-segment bar underneath the life icons visualizes the cooldown. A fully
lit bar means the blaster is ready. Bullets that leave the top of the screen are
removed immediately.

## Fleets and levels

Aliens begin in a centered grid. The complete fleet moves horizontally in one
direction. When any alien reaches a screen edge, every alien drops by the
difficulty's configured distance and the fleet reverses direction.

When the final alien is destroyed:

1. A fleet-clear bonus is awarded.
2. The level increases.
3. The ship is centered and active bullets are cleared.
4. A new, faster fleet is created.

Fleet creation accounts for the selected resolution, keeping the formation
centered and preventing aliens from spawning outside smaller windows.

## Scoring

The base award is 50 points per alien and 250 points per cleared fleet. Both are
multiplied by the current level and selected difficulty multiplier.

The HUD displays:

- remaining ships at the upper left;
- the blaster cooldown directly below the ships;
- Time Attack time remaining when applicable;
- saved high score near the top center;
- current score and level at the upper right.

## Ship impacts and game over

An impact occurs when an alien touches the ship or reaches the bottom of the
screen. Combat pauses and a short pixel-particle explosion plays without
blocking the application.

After the effect finishes, one ship is removed. If ships remain, the player is
given a brief recovery period before a fresh fleet appears. Otherwise, the game
ends and presents Play Again and Main Menu controls.

## Pause behavior

Escape freezes the complete simulation, including movement, bullet cooldown,
explosions, recovery, and the Time Attack clock. The pause menu provides Resume,
Restart, and Main Menu actions.

## Display settings

The Settings screen supports 800×600, 1200×800, and 1600×900 resolutions. It
also provides three procedural themes:

- **Earth Orbit:** deep navy space and a blue atmospheric glow;
- **Deep Space:** a darker field with brighter stars;
- **Purple Nebula:** a purple-tinted atmosphere and star palette.

The star fields are generated from a deterministic seed, so the same theme and
resolution always produce the same background.

## Persistence

The game saves preferences, the last selected game options, and a separate high
score for every mode-and-difficulty combination. Writes use a temporary file
followed by an atomic replacement to reduce the chance of leaving partial save
data. Invalid or corrupted values are ignored and replaced with safe defaults.
