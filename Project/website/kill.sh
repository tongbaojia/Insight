kill -9 `cat save_pid.txt`
rm save_pid.txt
ps aux | grep python
