import { Routes } from '@angular/router';
import { GenerationComponent } from './generation/generation.component';
import { ConfigurationsComponent } from './configurations/configurations.component';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'generation',
    pathMatch: 'full'
  },
  {
    path: 'configurations',
    component: ConfigurationsComponent
  },
  {
    path: 'generation',
    component: GenerationComponent
  }
];