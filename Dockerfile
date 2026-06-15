FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy only the necessary frontend files to serve
COPY index.html /usr/share/nginx/html/
COPY matches.js /usr/share/nginx/html/
COPY sources.js /usr/share/nginx/html/

# Expose port 80 (Railway will automatically detect and route to this port)
EXPOSE 80