import { CommonModule } from '@angular/common';
import { Component, computed, signal } from '@angular/core';

interface HelpItem {
  question: string;
  answer: string;
}

interface HelpSection {
  id: string;
  title: string;
  icon: string;
  items: HelpItem[];
}

@Component({
  selector: 'app-help-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './help-page.component.html',
})
export class HelpPageComponent {
  readonly activeSection = signal<string>('inicio');
  readonly openItems = signal<Set<string>>(new Set());

  readonly sections: HelpSection[] = [
    {
      id: 'inicio',
      title: 'Primeros pasos',
      icon: '🚀',
      items: [
        {
          question: '¿Cómo empiezo a usar la aplicación?',
          answer:
            'Tras iniciar sesión, accede al Dashboard para ver el resumen financiero. Desde ahí puedes navegar a cualquier sección usando el menú lateral o el buscador rápido (Ctrl+K en Windows / Cmd+K en Mac).',
        },
        {
          question: '¿Cómo navego rápidamente entre secciones?',
          answer:
            'Usa el atajo de teclado Ctrl+K (Windows) o Cmd+K (Mac) para abrir el buscador rápido. Escribe el nombre de la sección a la que quieres ir y pulsa Enter.',
        },
        {
          question: '¿Cómo recupero mi contraseña si la olvidé?',
          answer:
            'En la pantalla de inicio de sesión, haz clic en "¿Olvidaste tu contraseña?". Introduce tu email y recibirás un enlace para crear una nueva contraseña. El enlace caduca en 1 hora.',
        },
      ],
    },
    {
      id: 'documentos',
      title: 'Documentos e IA',
      icon: '📄',
      items: [
        {
          question: '¿Qué tipos de archivo puedo subir?',
          answer:
            'Puedes subir PDFs, imágenes (JPG, PNG) y documentos de texto. La IA extrae automáticamente los datos financieros de facturas y tickets.',
        },
        {
          question: '¿Qué ocurre cuando subo un documento?',
          answer:
            'El sistema lo procesa automáticamente con IA. Verás un indicador mientras procesa. Cuando termine, te redirigirá a Control Total (IA) para que revises y valides los datos extraídos.',
        },
        {
          question: '¿Qué hago si la IA extrae datos incorrectos?',
          answer:
            'Ve a Control Total (IA), localiza el registro y haz clic en el icono de lápiz para editarlo. Corrige los campos que estén mal y márcalo como revisado cuando esté correcto.',
        },
        {
          question: '¿Puedo reprocesar un documento con error?',
          answer:
            'Sí. En el detalle del documento, si el procesamiento falló, verás un botón "Reintentar". Haz clic y el sistema volverá a intentar extraer los datos.',
        },
      ],
    },
    {
      id: 'movimientos',
      title: 'Movimientos financieros',
      icon: '💸',
      items: [
        {
          question: '¿Cuál es la diferencia entre las secciones de movimientos?',
          answer:
            '"Movimientos financieros" muestra todos los movimientos del sistema (de cualquier origen). "Movimientos sin factura" es para registrar gastos manuales o importar desde Excel cuando no hay factura.',
        },
        {
          question: '¿Cómo registro un gasto sin factura?',
          answer:
            'Ve a "Movimientos sin factura" → pestaña "Entrada manual". Rellena el formulario con fecha, tipo, concepto, tercero e importes. Haz clic en "Registrar movimiento".',
        },
        {
          question: '¿Puedo importar movimientos desde Excel?',
          answer:
            'Sí. En "Movimientos sin factura" → pestaña "Importar Excel". Sube un archivo .xlsx con tus registros. Los duplicados se detectan y omiten automáticamente.',
        },
        {
          question: '¿Cómo corrijo un movimiento registrado incorrectamente?',
          answer:
            'En "Movimientos financieros", haz clic en el icono de lápiz (✏️) de la fila que quieres editar. Se abrirá un panel lateral con todos los campos editables. Guarda los cambios cuando termines.',
        },
        {
          question: '¿Para qué sirve la bandera de "Necesita revisión"?',
          answer:
            'Es una marca que la IA añade cuando no está segura de los datos extraídos. Te ayuda a identificar rápidamente qué movimientos debes verificar manualmente.',
        },
      ],
    },
    {
      id: 'dashboard',
      title: 'Dashboard y exportación',
      icon: '📊',
      items: [
        {
          question: '¿Qué muestra el Dashboard?',
          answer:
            'El Dashboard muestra un resumen financiero con ingresos, gastos, beneficio neto, balance de IVA, flujo mensual, gastos por categoría y top proveedores/clientes según el período seleccionado.',
        },
        {
          question: '¿Cómo filtro por período en el Dashboard?',
          answer:
            'Usa los filtros de fecha (Desde / Hasta) en la parte superior del Dashboard. Los gráficos y KPIs se actualizan automáticamente al cambiar las fechas.',
        },
        {
          question: '¿Cómo exporto los datos a Excel?',
          answer:
            'En el Dashboard, configura el período deseado y haz clic en "Exportar Excel". El archivo descargado incluye tablas de datos y gráficas de todos los indicadores.',
        },
      ],
    },
    {
      id: 'equipo',
      title: 'Equipo y usuarios',
      icon: '👥',
      items: [
        {
          question: '¿Cómo invito a un compañero?',
          answer:
            'Ve a "Miembros e invitaciones", escribe el email de la persona en el campo de invitación y envíala. El usuario recibirá un correo con un enlace para unirse a tu empresa.',
        },
        {
          question: '¿Cuántos usuarios puedo invitar?',
          answer:
            'No hay límite en el número de miembros. Puedes invitar a tantas personas como necesites.',
        },
        {
          question: '¿Cómo cambio mi contraseña?',
          answer:
            'Cierra sesión y, en la pantalla de inicio de sesión, haz clic en "¿Olvidaste tu contraseña?". Sigue el proceso de recuperación con tu email.',
        },
      ],
    },
  ];

  readonly currentSection = computed(
    () => this.sections.find((s) => s.id === this.activeSection()) ?? this.sections[0]
  );

  setSection(id: string): void {
    this.activeSection.set(id);
    this.openItems.set(new Set()); // reset accordions on section change
  }

  toggleItem(key: string): void {
    const current = new Set(this.openItems());
    if (current.has(key)) {
      current.delete(key);
    } else {
      current.add(key);
    }
    this.openItems.set(current);
  }

  isOpen(key: string): boolean {
    return this.openItems().has(key);
  }

  itemKey(sectionId: string, question: string): string {
    return `${sectionId}::${question}`;
  }
}
