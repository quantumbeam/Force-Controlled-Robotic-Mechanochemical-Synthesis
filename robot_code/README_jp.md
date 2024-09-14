### Robotic Powder Grinding for Laboratory Automation
<img src="https://github.com/quantumbeam/powder_grinding/blob/main/wiki/grinding_demo.gif?raw=true" alt="UR powder grinding" width="500">

乳棒と乳鉢用いたロボットメカノケミカル合成のためのROSパッケージです。
シミュレーション(Gazebo)上での動作とロボット実機での動作ができます。

## 目次
- [目次](#目次)
- [対応ロボット](#対応ロボット)
- [クイックスタート](#クイックスタート)
  - [PCとロボットとDocker環境のセットアップ](#pcとロボットとdocker環境のセットアップ)
  - [Dockerコンテナの立ち上げ](#dockerコンテナの立ち上げ)
  - [Dockerコンテナ内でのROS環境のビルド](#dockerコンテナ内でのros環境のビルド)
  - [モーションのデモ](#モーションのデモ)
- [License](#license)



## 対応ロボット
- UR5e


## クイックスタート

### PCとロボットとDocker環境のセットアップ
- [環境セットアップの資料](./env/docker/README_jp.md)を読んで環境セットアップし、終わったらこちらに戻ってきて以下の続きを実行してください。

### Dockerコンテナの立ち上げ
- ターミナル内でのDockerコンテナの立ち上げ
   - `cd ./env && ./RUN-DOCKER-CONTAINER.sh`
- Terminatorによる複数ターミナルの起動とDockerコンテナの立ち上げ
   - `cd ./env && ./LAUNCH-TERMINATOR-TERMINAL.sh`
      - 立ち上げられた複数ターミナルでは`RUN-DOCKER-CONTAINER.sh`が自動実行されている。

### Dockerコンテナ内でのROS環境のビルド
- 初回のみ実行
   - `./INITIAL_SETUP_ROS_ENVIROMENTS.sh`  
- 通常時のビルド
   - `./BUILD_ROS_WORKSPACE.sh`
-  以上のコマンドは`catkin_ws` のディレクトリ内で実行すること(`RUN-DOCKER-CONTAINER.sh`実行時はデフォルトで`catkin_ws`に入っている。)

### モーションのデモ
- UR5e、cobottaの立ち上げと粉砕モーションのデモファイルを用意しています。
- ロボットの立ち上げ
   ```
   roslaunch grinding_robot_bringup ur5e_bringup.launch
   ```
   - シミュレーション使う場合は`sim:=true`で立ち上げてください。
- 粉砕モーションの立ち上げ
   ```
   roslaunch grinding_motion_routines ur5e_grinding_demo.launch

   ```
   - コマンド`g`で粉砕の実行準備(g=grinding)、続けて`y`で粉砕実行します。
   - コマンド`G`でヘラによる粉集めの実行準備(g=grinding)、続けて`y`で粉集め実行します。
- 粉砕パラメータの設定
   -  grinding_motion_routinesパッケージ内のconfig内に設定があります。

## License
This repository is under the MIT license. See [LICENSE](./LICENSE) for details.
