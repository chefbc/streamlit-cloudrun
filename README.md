# Build and deploy

Command to build the application. PLease remeber to change the project name and application name
```
gcloud builds submit --tag gcr.io/<ProjectName>/<AppName>  --project=<ProjectName>
```



gcloud builds submit --tag gcr.io/chefbc/streamlit  --project=chefbc

Command to deploy the application
```
gcloud run deploy --image gcr.io/<ProjectName>/<AppName> --platform managed  --project=<ProjectName> --allow-unauthenticated
```

gcloud run deploy streamlit \
--image gcr.io/chefbc/streamlit \
--platform managed \
--project=chefbc \
--allow-unauthenticated \
--region=us-central1 \
--service-account=pv-calendar@chefbc.iam.gserviceaccount.com
