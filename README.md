# GHGA Microservice Cookiecutter Template

This is a cookiecutter template for GHGA microservice repositories. Use as follows:
```
cookiecutter gh:ghga-de/microservice-repository-template
```

The cookiecutter template requests the following information from the user:

* `project_name`<br>
Default: `My Microservice`<br>
*A project name, may contain spaces*
* `project_slug`<br>
Default: Lower-case, underscore-separated version of `project_name`<br>
*The Python project slug, i.e. module name. Must contain only underscores (_) as a word separator*
* `project_short_description`<br>
Default: `A microservice for GHGA`<br>
*A brief description of the microservice*
* `ghga_chassis_lib_version`<br>
Default: `0.9.0`<br>
*The GHGA chassis lib version to be used by the microservice*
* `ghga_chassis_lib_extras`<br>
Default: `api,pubsub,mongo_connect,object_storage_dao,s3,postgresql`<br>
*The extras to include when including the GHGA chassis lib. Must be a comma separated list of valid extra names.*
* `use_alembic`<br>
Default: `y`<br>
*Whether or not to enable database migration in this repository, typically should be 'y' for every service using a relational database.
* `config_bases`<br>
Default: `ApiConfigBase, PubSubConfigBase, PostgresqlConfigBase, S3ConfigBase`<br>
*A list of base classes to inherit from when defining the Config class. Must be a comma separated list of config base class names.*
