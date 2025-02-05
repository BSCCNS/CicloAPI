# Use an official Python runtime as a parent image
FROM gboeing/osmnx

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY dist/ .

COPY src/cicloapi/data/users_db_fake.json /app/src/cicloapi/data/

# Install the Python dependencies
RUN uv pip install cicloapi-0.2-py3-none-any.whl --system

# Expose the port that the application will run on
EXPOSE 8000

# Command to run the application
CMD post_install && cicloapi