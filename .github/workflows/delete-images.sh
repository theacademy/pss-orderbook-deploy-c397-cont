#!/bin/bash

#seperating out the bash command for the delete-images workflow into its own shell script file 
#so that it runs all at once and not line by line? perhaps 

#...we'll see if this actually works 

allImages=$(aws ecr list-images --repository-name ${ECR_REPOSITORY} | grep imageTag | awk -F: '{gsub(" ", "\\n", $2); print $2}' | sed 's/\"//g' | grep ${COHORT}${TEAM} | head -n 10 )            
while [ -n "$allImages" ]
do
  for tagName in $(echo "$allImages" | head -n 10)
  do
    images="imageTag=$tagName $images"
  done
  if aws ecr batch-delete-image --repository-name ${ECR_REPOSITORY} --image-ids $images | grep "not found"           
  then
    exit 0
  fi
  images=""
  sleep 10
  allImages=$(aws ecr list-images --repository-name ${ECR_REPOSITORY} | grep imageTag | awk -F: '{gsub(" ", "\\n", $2); print $2}' | sed 's/\"//g' | grep ${COHORT}${TEAM} | head -n 10 )
  # allImages=""
done

#okay actually im not sure if i need this file at all 



              
