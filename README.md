## Edge Mesh Simulator 

### Setup
- Install dependencies:
	```sh
	pip install -r modules
	pnpm install --dir ./vis/ # OR npm install --prefix ./vis/ 
	```
- [Install docker engine](https://docs.docker.com/engine/install/) and compose
- Run `rmq.sh`. Now, as a separate process, execute `run.sh`. The app should now be accessible on `localhost:8000`.

### Navigation

<table><tr><td>

<kbd>T</kbd> - <u>**t**</u>op-down view

<kbd>R</kbd> - <u>**r**</u>eset camera

<kbd>B</kbd> - toggle <u>**b**</u>order box

<kbd>V</kbd> - toggle scene <u>**v**</u>isibility

<kbd>W</kbd>,<kbd>A</kbd>,<kbd>S</kbd>,<kbd>D</kbd> / arrow keys - pan

<kbd>Q</kbd>,<kbd>E</kbd> - orbit

Mouse - orbit/pan/zoom

<kbd>[</kbd>,<kbd>]</kbd> - signal visibility threshold

</td></tr></table>

### Development
- After making changes to the signal tracer:
	```sh
	cd ./sim/signal/ && python build.py build_ext --inplace --force
	```
