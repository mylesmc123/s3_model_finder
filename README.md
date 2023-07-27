# s3_model_finder
There is a AWS S3 containing buckets for multiple regions throughout the state of Louisiana that is having HEC-RAS Models built as part of the Louisiana Watershed Initiative (LWI). each region has an AWS S3 bucket containing HEC-RAS models that may be cataloged in various folder structures.

The app searches for HEC-RAS HDF plan files, and then downloads the most recent, extracts metadata and a model extent feature layer.

The data is then put into a Maplibre GL JS map and deployed to: https://lwi-aws-s3-hec-ras-models.onrender.com/

Clicking any polygon will display the metadata for the model associated with that feature layer.

![image](https://github.com/mylesmc123/s3_model_finder/assets/64209352/86bbc01a-4e0f-40ff-b61b-e8c1f5eff978)

