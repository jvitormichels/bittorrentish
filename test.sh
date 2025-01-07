#!/bin/bash

mkdir test_setup
cp RepeatedTimer.py test_setup/

for i in {1..4}; do
  cp client.py "test_setup/client_${i}.py"
  cp server.py "test_setup/server.py"
  sed -i "s/\"files\"/\"files_${i}\"/g" "test_setup/client_${i}.py"
  mkdir test_setup/files_${i}
done

for i in {1..10}; do
  touch "test_setup/files_1/${i}.txt"
done

for i in {11..16}; do
  touch "test_setup/files_2/${i}.txt"
done

cd test_setup

if [ "$1" = "tmux" ];
then
  gnome-terminal -- bash -c "
    tmux new-session -d -s torrent;

    tmux split-window -h;
    tmux split-window -h;
    tmux split-window -v;
    tmux select-pane -t 1;
    tmux split-window -v;

    tmux select-pane -t 0;
    tmux send-keys 'python3 server.py' C-m;

    tmux select-pane -t 1;
    tmux send-keys 'python3 client_1.py' C-m;

    tmux select-pane -t 2;
    tmux send-keys 'python3 client_2.py' C-m;

    tmux select-pane -t 3;
    tmux send-keys 'python3 client_3.py' C-m;

    tmux select-pane -t 4;
    tmux send-keys 'python3 client_4.py' C-m;

    tmux attach-session -d;
  ";
else
  gnome-terminal -- bash -c "python3 server.py;";
  gnome-terminal -- bash -c "python3 client_1.py;";
  gnome-terminal -- bash -c "python3 client_2.py;";
  gnome-terminal -- bash -c "python3 client_3.py;";
  gnome-terminal -- bash -c "python3 client_4.py;";
fi
