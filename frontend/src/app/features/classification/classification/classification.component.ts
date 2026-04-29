import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ClassificationService } from '../../../core/services/classification.service';

@Component({
  selector: 'app-classification',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './classification.component.html'
})
export class ClassificationComponent {

  selectedFile: File | null = null;
  previewUrl: string | null = null;
  loading = false;
  result: any = null;
  error = '';

  constructor(private classificationService: ClassificationService) {}

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (!file) return;

    this.selectedFile = file;

    const reader = new FileReader();
    reader.onload = () => {
      this.previewUrl = reader.result as string;
    };
    reader.readAsDataURL(file);
  }

  classify() {
    if (!this.selectedFile) return;

    this.loading = true;
    this.error = '';
    this.result = null;

    this.classificationService.classifyImage(this.selectedFile)
      .subscribe({
        next: (res) => {
          this.loading = false;
          this.result = res.data;
        },
        error: (err) => {
          this.loading = false;
          this.error = 'Error al clasificar la imagen';
          console.error(err);
        }
      });
  }
}