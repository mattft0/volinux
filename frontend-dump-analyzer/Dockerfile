FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY frontend-dump-analyzer/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY frontend-dump-analyzer/ .

# Build the application
RUN npm run build

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application
CMD ["npm", "start"] 