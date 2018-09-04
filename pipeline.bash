

#Run the tcga visualizer pipeline


docker run --rm  -u $UID -v /home/jgarrayo/TCGA_visualizer_data:/app/data tcga_validation \
	python validation.py -i /app/data/ACC.txt -r /app/data/public_ref.txt && \
docker run --rm -u $UID -v /home/jgarrayo/TCGA_visualizer_data:/app/data tcga_metrics \
	python compute_metrics.py -i /app/data/ACC.txt -c ACC BRCA -m /app/data/metrics_ref_datasets/ -p NEW_PARTICIPANT -o /app/data/data/ && \
docker run --rm -u $UID -v /home/jgarrayo/TCGA_visualizer_data:/app/data tcga_assessment \
	python manage_assessment_data.py -b /app/data/data/ -c ACC BRCA -p NEW_PARTICIPANT


#Build de imagenes:

#docker build -t tcga_validation .
#docker build -t tcga_metrics .
#docker build -t manage_assessment_data .
