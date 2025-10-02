import os
import pandas as pd
from deepface import DeepFace

def analyze_faces(image_folder='faceimages', output_file='output.csv'):
    """
    Analyze faces in images using DeepFace and save results to CSV.
    
    Args:
        image_folder (str): Path to folder containing images
        output_file (str): Path for output CSV file
    
    Returns:
        pd.DataFrame: DataFrame containing analysis results
    """
    # Create a list to store data for CSV
    csv_data = []
    
    # Check if image folder exists
    if not os.path.exists(image_folder):
        print(f"Error: Image folder '{image_folder}' not found.")
        return None
    
    # Get list of image files
    image_files = [f for f in os.listdir(image_folder) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
    
    if not image_files:
        print(f"No image files found in '{image_folder}'.")
        return None
    
    print(f"Found {len(image_files)} image(s) to process...")
    
    # Process each image in the folder
    for i, filename in enumerate(image_files, 1):
        image_path = os.path.join(image_folder, filename)
        print(f"Processing {i}/{len(image_files)}: {filename}")
        
        try:
            # Use deepface to get gender, race, and age
            result = DeepFace.analyze(image_path, actions=['gender', 'race', 'age'])
            
            # Extract gender, race, and age from the result
            gender = result[0]['gender']
            race = result[0]['dominant_race']
            age = result[0]['age']
            
            # Append data to the CSV list
            csv_data.append([filename, gender, race, age])
            print(f"  ✓ Gender: {gender}, Race: {race}, Age: {age}")
            
        except Exception as e:
            print(f"  ✗ Error processing image {filename}: {str(e)}")
            # Still add the filename with error info
            csv_data.append([filename, 'Error', 'Error', 'Error'])
    
    # Create a DataFrame from the CSV data
    columns = ['Filename', 'Gender', 'Race/Ethnicity', 'Age']
    df = pd.DataFrame(csv_data, columns=columns)
    
    # Write data to CSV file
    df.to_csv(output_file, index=False)
    print(f"\nCSV file '{output_file}' created successfully with {len(csv_data)} entries.")
    
    return df

def main():
    """Main function to run the face analyzer."""
    print("DeepFace Analyzer")
    print("================")
    
    # You can modify these paths as needed
    image_folder = 'faceimages'
    output_file = 'face_analysis_results.csv'
    
    # Run the analysis
    results_df = analyze_faces(image_folder, output_file)
    
    if results_df is not None:
        print(f"\nSummary:")
        print(f"Total images processed: {len(results_df)}")
        print(f"Successful analyses: {len(results_df[results_df['Gender'] != 'Error'])}")
        print(f"Errors: {len(results_df[results_df['Gender'] == 'Error'])}")

if __name__ == "__main__":
    main()
