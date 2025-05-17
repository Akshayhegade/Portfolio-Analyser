FROM node:19-alpine

WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies including devDependencies for build
RUN npm install --legacy-peer-deps

# Copy the rest of the frontend code
COPY . .

# Build the app
RUN npm run build

# Install serve to run the built app
RUN npm install -g serve

# Set environment variable for API URL
ENV REACT_APP_API_URL=http://localhost:5001

# Expose port 3000
EXPOSE 3000

# Start the app using serve for production
CMD ["serve", "-s", "build", "-l", "3000"]
