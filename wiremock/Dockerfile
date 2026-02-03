FROM wiremock/wiremock:latest

# Copy stub mappings and response files into the image
COPY mappings /home/wiremock/mappings
COPY __files /home/wiremock/__files

# Enable verbose logging and response templating
CMD ["--verbose", "--global-response-templating"]
