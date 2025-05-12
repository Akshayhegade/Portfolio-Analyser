FROM node:19-alpine

WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Set environment variable for API URL
# This will be used in the React app to connect to the backend
ENV REACT_APP_API_URL=http://localhost:5001

# Expose port 3000
EXPOSE 3000

# Start the app
CMD ["npm", "start"]
