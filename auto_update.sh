# $1 = python3 path
# $2 = git path
# $3 = working directory
# $4 = cron logs
# $5 = branch

{
  echo "START OF SCRIPT"
  date

  echo "#1 COMMAND: cd $3"
  cd $3 || exit

  echo "#2 COMMAND: pwd"
  pwd

  echo "#3 COMMAND: $2/git status"
  $2/git status

  echo "#4 COMMAND: $2/git checkout $5"
  $2/git checkout $5

  echo "#5 COMMAND: $2/git pull origin $5"
  $2/git pull origin $5

  echo "#6 COMMAND: python3 create-new-data.py data"
  $1/python3 create-new-data.py

  echo "#7 COMMAND: $2/git status"
  $2/git status

  echo "#8 COMMAND: $2/git add ."
  $2/git add .

  echo "#9 COMMAND: $2/git config credential.helper store"
  $2/git config credential.helper store

  echo '#10 COMMAND: $2/git commit -m "automatic update"'
  $2/git commit -m "automatic update"

  echo "#11 COMMAND: $2/git push origin $5"
  $2/git push origin $5

  date
  echo "END OF SCRIPT"
} >>$4/cron-log.txt
