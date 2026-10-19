import { Routes } from '@angular/router';
import { GenerationComponent } from './generation/generation.component';
import { ConfigurationsComponent } from './configurations/configurations.component';
import { TranspilationComponent } from './transpilation/transpilation.component';

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
  { path: 'transpilation', component: TranspilationComponent },
  {
    path: 'generation',
    component: GenerationComponent
  }
];