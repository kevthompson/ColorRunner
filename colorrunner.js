var gameover;
var playerColor;
var floorColor;
var offset;
var floorWidth;

function setup() {
    createCanvas(640, 480);
    background(200);
    floorWidth = 320;
    frameRate(60);
    playerColor = color(255, 0, 0);
    floorColor = [
            color(0, 0, 255),
            color(0, 255, 0),
            color(255, 0, 0),
        ];
    offset = 0;
    gameover = 0;
}

function draw() {
    if (gameover == 0) {
        stroke(0);
        fill(playerColor);
        rect(50, 380, 80, 80);

        for (var i = 0; i < 3; i++) {
            fill(floorColor[i]);
            rect(floorWidth * i - offset, 460, floorWidth, 20);
        }
        offset += 5;
        if (offset >= floorWidth) {
            var temp = floorColor[0];
            floorColor[0] = floorColor[1];
            floorColor[1] = floorColor[2];
            floorColor[2] = temp;
            offset = 0;
        }
        if (offset < 50 &&
            red(playerColor) == red(floorColor[0]) &&
            blue(playerColor) == blue(floorColor[0]) &&
            green(playerColor) == green(floorColor[0])) {
            setup();
        } else if (offset > floorWidth - 130 &&
            red(playerColor) == red(floorColor[1]) &&
            blue(playerColor) == blue(floorColor[1]) &&
            green(playerColor) == green(floorColor[1])) {
            setup();
        }
        if (keyIsPressed) {
            text(key, 30, 30);
        }
    } else {
        text("Game Over", 50, 50);
    }

}

function keyPressed() {
    if (keyCode == LEFT_ARROW) {
        playerColor = color(green(playerColor), blue(playerColor), red(playerColor));
    } else if (keyCode == RIGHT_ARROW) {
        playerColor = color(blue(playerColor), red(playerColor), green(playerColor));
    } else if (keyCode == ENTER) {
        setup();
    } else if (keyCode == BACKSPACE) {
        gameover = 1;
    }
}
