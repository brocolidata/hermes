# Brocolib CI/CD

## [CI Pipeline](CI_pipeline.yml)

This pipeline will run on response to all PRs newly opened or synchronized.
It will run pytests tests defined in the `/tests` folder.

 
## [CD Pipeline](CD_pipeline.yml)

This pipeline will run when you merge PRs on the `main` branch.
It will deploy a GitHub Release for every new versions of the package.