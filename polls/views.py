import io
import os
import sys

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic
from django.utils import timezone

from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as do_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout as do_logout
from django.contrib.auth.models import Group, User

from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.colors import pink, black, red, blue, green

from .models import Choice,Question,Questionarie
from random import random

TIPO=["estudiante","familia","tutoría","docente","pas"]
NUM=[31,31,1,99,30]

SUPERGR=["ESO1","ESO2","ESO3","ESO4","BACHD1","BACHD2","BACHN","FPB","INF","COM"]
GRUPOS=[
       ["ESO1A", "ESO1B", "ESO1C", "ESO1D"],
       ["ESO2A", "ESO2B", "ESO2C", "ESO2D", "PMAR1C", "PMAR1D"],
       ["ESO3A", "ESO3B", "ESO3C", "ESO3D", "PMAR2C", "PMAR2D"],
       ["ESO4A", "ESO4B", "ESO4C", "ESO4D"],
       ["BACHD1A", "BACHD1B", "BACHD1C"],
       ["BACHD2A", "BACHD2B", "BACHD2C"],
       ["BACHN1", "BACHN2", "BACHN3A", "BACHN3B"],
       ["FPBINF1", "FPBINF2","FPBCOM1", "FPBCOM2"],
       ["SMR1", "SMR2","SMRN1", "SMRN2", "DAM1", "DAM2","DAW1", "DAW2"],
       ["COM1", "COM2", "GES1", "GES2"]
       ]

M18=[ "GES1","GES2","DAM1","DAM2","DAW1","DAW2","BACHN1","BACHN2","BACHN3A","BACHN3B" ]

def votar(request,questionarie_id):
    Questionarie_selected=Questionarie.objects.get(pk=questionarie_id)
    if request.user.is_authenticated:
        if request.user.is_active:
            question_list=Questionarie_selected.question_set.all()
            for question in question_list: 
                c=str("")+str(question.id)+str("")
                if question.question_type == "Text":
                    res=question.question_answer+' ; usuario = '+request.user.username+' ; '+request.POST[c]
                    question.question_answer=res
                    question.save()
            for question in question_list:
                if question.question_type == "Choice" or question.question_type == "Choice4":
                    choice_list=question.choice_set.all()
                    try:
                        c=str("")+str(question.id)+str("")
                        selected_choice = question.choice_set.get(pk=request.POST[c])
                    except (KeyError, Choice.DoesNotExist):
                        error=1 
                        #no hacemos nada, tenemos en cuenta cuando hacemos el calculo de las que no se han respondido
                        #return render(request, 'polls/detail.html',{
                        #    'questionarie_id': questionarie_id,
                        #    'question_list': question_list,
                        #   'error_message': "You didn't select a choice.",
                        #   })
                        #print("error no exste selección")
                    else:
                        selected_choice.votes += 1
                        selected_choice.save()
            Questionarie_selected.total=0
            for question in question_list:
                if question.question_type == "Choice" or question.question_type == "Choice4":
                    question.total=0
                    valor_total=0
                    for choice in question.choice_set.all() :
                        question.total += choice.votes
                        valor_total=valor_total + float(choice.choice_text[0])*choice.votes
                    if question.total==0:
                       question.value = 0
                    else:
                       question.value = valor_total/question.total
                       
                    for choice in question.choice_set.all() :
                        if question.total==0:
                            choice.porc = 0.0
                        else:
                            choice.porc = choice.votes*100/question.total
                    if question.total > Questionarie_selected.total:
                        Questionarie_selected.total=question.total
                    question.save()
            Questionarie_selected.save()
            print('ntotal',question.total)
            if request.user.is_superuser :
                return render(request, 'polls/resultados.html',{
                'questionarie_id': questionarie_id,
                'question_list':  Questionarie_selected.question_set.all(),
                'error_message': "Error..",
                'questionarie_group': Questionarie_selected.questionarie_group,
                'ntotal': Questionarie_selected.total
                 })
            else :
                request.user.is_active=False
                request.user.save()
                # print("desactivmos el usuario "+str(request.user))
                return render(request, "polls/end.html")
    else:
       return redirect('/login')


#def duplicar(request,questionarie_id):
#    print(questionarie_id)
#    Q=Questionarie.objects.get(pk=questionarie_id)
#    print("vamos a duplicar "+Q.questionarie_text)
#    question_list=Q.question_set.all()
#    #print('questionarie_id=',questionarie_id)
#    #print(Questionarie.objects.all().count())
#    Q_new=Questionarie(questionarie_text=Q.questionarie_text, questionarie_group=Q.questionarie_group)
#    Q_new.save()
#    for q in question_list:
#        q_new = Q_new.question_set.create(question_text=q.question_text, pub_date=timezone.now(),question_type=q.question_type)
#        if q.question_type == "Choice":
#            for choice in q.choice_set.all():
#                q_new.choice_set.create(choice_text=choice.choice_text,votes=0)
#    return render(request, 'polls/detail.html',{
#        'questionarie_id': questionarie_id,
#         'question_list': question_list,
#         'error_message': "You didn't select a choice.",
#         })


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'questionarie_list'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                return Questionarie.objects.filter()
            else:
                if self.request.user.is_active:
                    #print("el usuario "+self.request.user.username+"; is_active = "+str(self.request.user.is_active)+"; first_name = "+self.request.user.first_name)
                    #todos los grupos a los que pertence el usuario
                    #for g in self.request.user.groups.all():
                    #    print(g)
                    # print(self.request.user.groups.all()[0])
                    #print(self.request.user.username)
                    #for j in Questionarie.objects.filter():
                    #    print(j.questionarie_group)
                    return Questionarie.objects.filter(questionarie_group=self.request.user.first_name)
                else:
                    return redirect('/login')
        else:
             return redirect('/login')

    #model = Question
#class DetailView(generic.DetailView, questionarie_id):
def DetailView(request,questionarie_id):
    if request.user.is_authenticated:
       q=Questionarie.objects.get(pk=questionarie_id)
       question_list=q.question_set.all()
       #print('questionarie_id=',questionarie_id)
       return render(request, 'polls/detail.html',{
           'questionarie_id': questionarie_id,
            'question_list': question_list,
            })
    else:
       return redirect('/login')


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def welcome(request):
    if request.user.is_authenticated:
        if request.user.first_name=='tutoría':
            user_list=[]
            user_list=User.objects.filter(first_name=request.user.username.split("_")[1])
 
            familias_list=[]
            for u in User.objects.filter(first_name='familia'):
                if u.username.split("_")[2]==request.user.username.split("_")[1]:
                    familias_list.append(u)

            return render(request, "polls/user.html",{
                'user_list':user_list,
                'familias_list':familias_list,
                })
        else:
            return render(request, "polls/welcome.html")
    return redirect('/login')



def login(request):
    # Creamos el formulario de autenticación vacío
    form = AuthenticationForm()
    if request.method == "POST":
        # Añadimos los datos recibidos al formulario
        form = AuthenticationForm(data=request.POST)
        # Si el formulario es válido...
        if form.is_valid():
            # Recuperamos las credenciales validadas
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Verificamos las credenciales del usuario
            user = authenticate(username=username, password=password)

            # Si existe un usuario con ese nombre y contraseña
            if user is not None:
                # Hacemos el login manualmente
                do_login(request, user)
                # Y le redireccionamos a la portada
                return redirect('/')

    # Si llegamos al final renderizamos el formulario
    return render(request, "polls/login.html", {'form': form})

def logout(request):
    # Finalizamos la sesión
    do_logout(request)
    # Redireccionamos a la portada
    return redirect('/')


def activar_usuarios(request):
   for i in User.objects.all():
      if not i.is_active:
         print(i.username+" "+str(i.is_active))
         i.is_active=True
         i.save()
   return render(request, "polls/welcome.html")


def view_pdf(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    ini=810
    xini=15
    nline=ini
    h=75
    a=190
    i=0


    if request.user.is_authenticated:
        if request.user.username=='madrid':
            user_list=[]
            for u in User.objects.filter():
                if u.username.split("_")[0]=="tutoría":
                    user_list.append(u)
            for u in User.objects.filter():
                if u.username.split("_")[0]=="docente":
                    user_list.append(u)
            for u in User.objects.filter():
                if u.username.split("_")[0]=="pas":
                    user_list.append(u)


            for u in user_list:
                #print(u.username) 
                p.rect(xini+a*(i%3),nline-h+20,a,h)
                p.drawString(10+xini+a*(i%3),nline, "https://encuestas.iesquevedo.es")
                p.drawString(10+xini+a*(i%3),nline-20, u.username)
                p.drawString(10+xini+a*(i%3),nline-40,"contraseña "+u.last_name)
                if i%3 == 2 :
                    nline=nline-h
                i=i+1
                if i == 11*3:
                    p.showPage()
                    nline=ini
                    i=0
            p.showPage()



        if request.user.first_name=='tutoría':
            user_list=User.objects.filter(first_name=request.user.username.split("_")[1])
            print(user_list)
            familias_list=[]
            for u in User.objects.filter(first_name='familia'):
                print( u.username,request.user.username)
                if u.username.split("_")[2]==request.user.username.split("_")[1]:
                    familias_list.append(u)
            p.drawString(30, 800, "https://encuestas.iesquevedo.es")
            nline=770
            for u in user_list:
                p.drawString(30,nline, u.username)
                p.drawString(160,nline, u.last_name)
                nline=nline-22
            p.showPage()

            i=0
            nline=ini
            for u in familias_list:
                #print(u.username,(i%3),nline) 
                p.rect(xini+a*(i%3),nline-h+20,a,h)
                p.drawString(10+xini+a*(i%3),nline, "https://encuestas.iesquevedo.es")
                p.drawString(10+xini+a*(i%3),nline-20, u.username)
                p.drawString(10+xini+a*(i%3),nline-40,"contraseña "+u.last_name)
                if i%3 == 2 :
                    nline=nline-h
                i=i+1
                if i == 11*3:
                    p.showPage()
                    nline=ini
            if i > 0 :
                p.showPage()

    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='test.pdf')


def gestion_encuestas(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
          return render(request, "polls/crear_encuestas.html")     
        else:
          return render(request, "polls/welcome.html")
    return redirect('/login')


def crear_usuarios(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            all_user=[]
            for i in range(0,len(TIPO)):
              for j in range(0,NUM[i]):
                name=str(TIPO[i])
                if(TIPO[i] != "tutoría"):
                  name=name+"_"
                if (j<10) and (TIPO[i] != "tutoría") :
                  name=name+"0"
                if(TIPO[i] != "tutoría"):
                  name=name+str(j)
                if((TIPO[i]=="docente") or (TIPO[i]=="pas") ):
                  all_user.append(name)
                else: #caso estudiante familia tutoría
                  for GR in GRUPOS:
                    for g in GR:
                      name_curso=name+"_"+str(g)
                      if(not((TIPO[i] == "familia") and (g in M18))):
                        all_user.append(name_curso)  
            new_user=[]
            for name in all_user:
              crear_usuario=True
              for u in User.objects.all():
                if(name == u.username): 
                  crear_usuario=False
            
              if(crear_usuario):
                new_user.append(name)  
                passw=str(random()*10000000000)[0:4]
                user=User.objects.create_user(name, password=passw)
                user.is_superuser=False
                user.is_staff=False
                user.is_active=True
                if(name.split("_")[0]=="estudiante"):
                  user.first_name=name.split("_")[2]
                else:
                  user.first_name=name.split("_")[0]
                user.last_name=passw
                user.save()
                print("creamos el usuario "+name+" "+passw)
              else:
                print("el usuario "+name+" ya existe, no lo creamos")

 
            return render(request, "polls/crear_usuarios.html",{
                'user_list':new_user,
                })
        else:
          return render(request, "polls/welcome.html")
    return redirect('/login')


def crear_usuarios_definitivo(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            print("usuarios creados")
            return render(request, "polls/welcome.html")
        else:
            return render(request, "polls/welcome.html")
    else:
        return redirect('/login')

def cambiar_passwd(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            borrar_usuarios=[]
            for u in User.objects.all():
                if((u.username.split("_")[0]=="familia") | (u.username.split("_")[0]=="estudiante") | (u.username.split("_")[0]=="pas") | (u.username.split("_")[0]=="tutoría") | (u.username.split("_")[0]=="docente")):
                    borrar_usuarios.append(u)

            return render(request, "polls/cambiar_passwd.html",{
                'user_list':borrar_usuarios,
                })
        else:
            return render(request, "polls/welcome.html")
    return redirect('/login')

def cambiar_passwd_definitivo(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            for u in User.objects.all():
                if((u.username.split("_")[0]=="familia") | (u.username.split("_")[0]=="estudiante") | (u.username.split("_")[0]=="pas") | (u.username.split("_")[0]=="tutoría") | (u.username.split("_")[0]=="docente")):
                    new_passwd=str(random()*10000000000)[0:4]
                    u.set_password(new_passwd)
                    u.last_name=new_passwd
                    u.save()
                    print("cambiamos la contraseña de ",u.username," por ",new_passwd)
       



def gestion_usuarios(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            user_list=User.objects.all()
            familias_list=[]
            for u in User.objects.filter(first_name='familia'):
                familias_list.append(u)

            return render(request, "polls/gestion_usuarios.html",{
                'user_list':user_list,
                'familias_list':familias_list,
                })
        else:
            return render(request, "polls/welcome.html")
    return redirect('/login')


def resultados(request,questionarie_id):
    if request.user.is_superuser:
        return render(request, 'polls/resultados.html',{
        'questionarie_id': questionarie_id,
        'question_list':  Questionarie.objects.get(pk=questionarie_id).question_set.all(),
        'error_message': "Error..",
        'questionarie_group': Questionarie.objects.get(pk=questionarie_id).questionarie_group,
        'ntotal': Questionarie.objects.get(pk=questionarie_id).total 
        })


def grupo_resultados(request):
    
    resultado=[]
    valor_medio=[]

    media=[["Resumen del cuestionario para la evaluación del instituto"],["Nº de estudiantes que han contestado"]]
    media_nrespuestas=[["Resumen del cuestionario para la evaluación del instituto"],["Nº de estudiantes que han contestado"]]

    for i in SUPERGR:
        media[0].append(i)
        media_nrespuestas[0].append(i)


    for q in Questionarie.objects.get(questionarie_group="ESO1A").question_set.all():
        if q.question_text!="OBSERVACIONES":
            aux3=[]
            aux3.append(q.question_text)
            aux4=[]
            aux4.append(q.question_text)
            for j in range(len(GRUPOS)):
                aux3.append("0")
                aux4.append("0")
            media.append(aux3)
            media_nrespuestas.append(aux4)


    #print(media) 
    imedia=1
#    for lista in [["FPB1", "FPB2"]]:
    for lista in GRUPOS: 
        informe=[["Cuestionario para la evaluación del instituto"],["Nº de estudiantes que han contestado"]]
        for q in Questionarie.objects.get(questionarie_group="ESO1A").question_set.all():
            if q.question_text=="OBSERVACIONES":
                aux=[]
                aux.append(q.question_text)
                informe.append(aux)
                for i in q.question_answer.split("usuario ="):
                    aux=[]
                    aux.append(i)
                    informe.append(aux)

            else:    
                aux=[]
                aux.append(q.question_text)
                informe.append(aux)

        total_media=0
        
        for g in lista:
            informe[0][0]=informe[0][0]+" "+g
            informe[0].append(g)
            informe[1].append(Questionarie.objects.get(questionarie_group=g).total)

            total_media=total_media+Questionarie.objects.get(questionarie_group=g).total
           
            i=2
            
            for q in Questionarie.objects.get(questionarie_group=g).question_set.all():
                if q.question_type=="Label":
                    informe[i].append("")
                    media[i][imedia]=""
                    media_nrespuestas[i][imedia]=""
                else:
                    informe[i].append(q.value)
                    if q.question_text!="OBSERVACIONES":
                        if int(q.total) != 0:
                            media[i][imedia]=str(float(media[i][imedia])+float(q.value)*float(q.total))
                            media_nrespuestas[i][imedia]=str(float(media_nrespuestas[i][imedia])+float(q.total))
                    else:
                        for u in q.question_answer.split("usuario ="):
                            aux=[]
                            aux.append(u+g)
                            informe.append(aux)
#                            if q.question_text=="OBSERVACIONES":
#                    for i in q.question_answer.split("usuario ="):
#                        aux=[]
#                        aux.append(i)
#                        informe[0].append(aux)
#

                i=i+1

        i=2
        for q in Questionarie.objects.get(questionarie_group=g).question_set.all():
            if q.question_type !="Label" and q.question_text!="OBSERVACIONES" and float(media_nrespuestas[i][imedia]) > 0.0:
                #print(media[i][imedia],media_nrespuestas[i][imedia])
                media[i][imedia]=str(str((float(media[i][imedia])/float(media_nrespuestas[i][imedia])))+str(0000))[0:4]
            i=i+1


        media[1].append(total_media)
        #print("total_media ="+str(total_media))

        resultado.append(informe)    
        imedia=imedia+1
    valor_medio.append(media)

    if request.user.is_superuser:
        return render(request, 'polls/grupo_resultados.html',{
        'resultado': resultado,
        'valor_medio': valor_medio,
        'error_message': "Error..",
        })
    

def crear_encuestas_alumnos():
  for GR in GRUPOS:
    for g in GR:
      crear=True
      for q in Questionarie.objects.all():
        if q.questionarie_group==g:
          crear=False
          print("No creamos la encuesta para : "+q.questionarie_group) 
      if crear: 
        print("Creamos la encuesta para : "+g) 
  
        Q_new=Questionarie(questionarie_text="Cuestionario para la evaluación del instituto ("+g+")",questionarie_group=g)
        Q_new.save()
  
        Q_new.question_set.create(question_text="CENTRO (1. Nunca, 2. Casi nunca, 3. Casi siempre, 4. Siempre)", pub_date=timezone.now(),question_type="Label")
    
        lista_preguntas01 = [
          "1 Te satisface pertenecer al Centro",
          "2 Estoy satisfecho con las instalaciones y el mantenimiento del Centro",
          "3 Estoy satisfecho con el estado, limpieza y decoración de mi aula",
          "4 He utilizado voluntariamente las instalaciones: biblioteca (mañana y tarde), pistas deportivas, cafetería",
          "5 Respeto y colaboro en las normas del Centro, así como en el buen uso de los espacios y materiales",
          "6 Estoy satisfecho con las actividades extraescolares de tarde: Deportes, Refuerzo, Teatro ",
          "7 Conozco y/o utilizo las actividades del APA por la tarde: baile, danza, ping-pong, taller inglés, Técnicas Estudio, etc.",
          "8 Conozco y/o utilizo las actividades que se proponen durante los recreos: talleres, juegos de mesa, liguillas deportivas",
          "9 Estoy satisfecho con los talleres y charlas de monitores externos (policía, educadores sociales, médicos/enfermeras, etc.)",
          "10 Estoy satisfecho con las actividades escolares fuera del centro por las mañanas (museos, teatro, cine, excursiones culturales)",
          "11 Estoy satisfecho con la oferta de viajes que realiza el Centro (Cantabria, Italia, Francia, Gran Bretaña, otros)",
          "12 Dirección y Jefatura de Estudios me atienden si lo necesito",
          "13 He recibido orientación y ayuda del Departamento de Orientación cuando ha sido necesario",
          "14 La Agenda me resulta útil a lo largo del curso"]
    
        lista_preguntas02 = [
          "15 El tutor/a nos ayuda y se preocupa a lo largo del curso",
          "16 El profesorado se preocupa por la formación en valores: solidaridad, justicia, tolerancia, responsabilidad, etc.",
          "17 Considero que mi comportamiento es respetuoso con el profesorado y el personal del Centro",
          "18 Las actuaciones del profesorado son parecidas en: disciplina, puntualidad, asistencia, evaluación, resolución de conflictos, etc.",
          "19 El profesorado me atiende y me orienta cuando planteo alguna dificultad o duda.",
          "20 Mis profesores me enseñan cómo estudiar (Técnicas/Estrategias de Estudio)"]
    
    
    
        for a in lista_preguntas01:
          q_new = Q_new.question_set.create(question_text=a, pub_date=timezone.now(),question_type="Choice4")
          for choice in ["1. Nunca","2. Casi nunca","3. Casi siempre","4. Siempre"]:
            q_new.choice_set.create(choice_text=choice,votes=0)
            
        Q_new.question_set.create(question_text="PROFESORADO (1. Nunca, 2. Casi nunca, 3. Casi siempre, 4. Siempre)", pub_date=timezone.now(),question_type="Label")
        for a in lista_preguntas02:
          q_new = Q_new.question_set.create(question_text=a, pub_date=timezone.now(),question_type="Choice4")
          for choice in ["1. Nunca","2. Casi nunca","3. Casi siempre","4. Siempre"]:
              q_new.choice_set.create(choice_text=choice,votes=0)
    
        q_new = Q_new.question_set.create(question_text="COMPAÑEROS (1. Nunca, 2. Casi nunca, 3. Casi siempre, 4. Siempre)", pub_date=timezone.now(),question_type="Label")
        for a in [
          "21 Considero que mi comportamiento es respetuoso con  los compañer@s",
          "22 Siento que mis compañer@s me respetan",
          "23 El delegado/a de clase ha hecho bien su trabajo"]:
          q_new = Q_new.question_set.create(question_text=a, pub_date=timezone.now(),question_type="Choice4")
          for choice in ["1. Nunca","2. Casi nunca","3. Casi siempre","4. Siempre"]:
              q_new.choice_set.create(choice_text=choice,votes=0)
    
        for a in ["24 He sido testigo de cómo un compañero/a trataba mal a otro/a","25 Conozco a algún alumn@ mediador del centro y su labor"]:
          q_new = Q_new.question_set.create(question_text=a+" (1.Si 2.No)", pub_date=timezone.now(),question_type="Choice")
          for choice in ["1. Si","2. No"]:
              q_new.choice_set.create(choice_text=choice,votes=0)
    
        a="OPINIÓN GLOBAL SOBRE EL CENTRO"
        q_new = Q_new.question_set.create(question_text=a+" (1.M 2.R 3.B 4.MB)", pub_date=timezone.now(),question_type="Choice")
        for choice in ["1. MALO","2. REGULAR","3. BUENO","4. MUY BUENO"]:
          q_new.choice_set.create(choice_text=choice,votes=0)
        Q_new.question_set.create(question_text="OBSERVACIONES", pub_date=timezone.now(),question_type="Text")
 
def crear_encuestas_docentes():
  g="docente"
  crear=True
  for q in Questionarie.objects.all():
    if q.questionarie_group==g:
      crear=False
      print("No creamos la encuesta para : "+q.questionarie_group) 
  if crear: 
    print("Creamos la encuesta para : "+g) 

    Q_new=Questionarie(questionarie_text="Cuestionario para la evaluación del instituto", questionarie_group=g)
    Q_new.save()

#    Q_new.question_set.create(question_text="Cuestionario para la evaluación del instituto",pub_date=timezone.now(),question_type="Label")
    Q_new.question_set.create(question_text="1. En desacuerdo, 2. Poco de acuerdo, 3. De acuerdo, 4. Totalmente de acuerdo", pub_date=timezone.now(),question_type="Label")

    lista_preguntas01 = [
        "1 Estoy satisfecho con el ambiente y el clima del Centro",
        "2 Siento que mi trabajo tiene valor",
        "3 La comunicación con el Equipo Directivo es fácil",
        "4 El Equipo Directivo organiza correctamente la distribución de recursos: biblioteca, aulas informática, espacios varios, guardias, tablets…)",
        "5 Cuando se comparten con los compañeros las experiencias profesionales, éstos muestran interés y se promueve un clima de intercambio",
        "6 La relación entre el personal no docente y el profesorado es productiva",
        "7 Mi relación con las familias es productiva",
        "8 Estoy satisfecho con el alumnado del Centro",
        "9 Conozco, comparto y/o participo en los proyectos institucionales del Centro (4º+Empresa, Erasmus+, Google Classrooms, Emprendimiento, otros)",
        "10 El profesorado puede participar en la toma de decisiones",
        "11 Hay buen ambiente de trabajo en el Departamento Didáctico",
        "12 El Equipo Directivo se interesa personalmente por los problemas que tienen algunos profesores en el aula",
        "13 Recibo un trato justo y equitativo por la dirección del Centro",
        "14 Creo que es necesario que el centro cree un Plan de Mejora para todos",
        "15 Conozco la planificación y la estrategia del Centro tanto por parte del Equipo Directivo como de los órganos de coordinación y de otros responsables del Centro",
        "16 Las actuaciones del profesorado están coordinadas por el departamento en cuanto a los procesos de enseñanza-aprendizaje y evaluación",
        "17 Las actuaciones del profesorado son parecidas en cuanto a: disciplina, puntualidad, asistencia, evaluación, resolución de conflictos, etc..",
        "18 El desarrollo de la actividad en mi clase respeta los diferentes ritmos de aprendizaje de los alumnos",
        "19 El profesorado informa a los alumnos acerca de su progreso continuo en los aprendizajes"]

    for a in lista_preguntas01:
        q_new = Q_new.question_set.create(question_text=a, pub_date=timezone.now(),question_type="Choice4")
        for choice in ["1. En desacuerdo","2. Poco de acuerdo","3. De acuerdo", "4. Totalmente de acuerdo"]:
            q_new.choice_set.create(choice_text=choice,votes=0)
        
#    Q_new.question_set.create(question_text="CUESTIONES", pub_date=timezone.now(),question_type="Label")

    a="OPINIÓN GLOBAL SOBRE EL CENTRO (1.M 2.R 3.B 4.MB)"
    q_new = Q_new.question_set.create(question_text=a, pub_date=timezone.now(),question_type="Choice")
    for choice in ["1. MALO","2. REGULAR","3. BUENO","4. MUY BUENO"]:
        q_new.choice_set.create(choice_text=choice,votes=0)
    Q_new.question_set.create(question_text="OBSERVACIONES", pub_date=timezone.now(),question_type="Text")


def crear_encuestas_familia():
  g="familia"
  crear=True
  for q in Questionarie.objects.all():
    if q.questionarie_group==g:
      crear=False
      print("No creamos la encuesta para : "+q.questionarie_group)
  if crear:
    print("Creamos la encuesta para : "+g)

    Q_new=Questionarie(questionarie_text="Cuestionario para la evaluación del instituto", questionarie_group=g)
    Q_new.save()

#    Q_new.question_set.create(question_text="Cuestionario para la evaluación del instituto",pub_date=timezone.now(),question_type="Label")
    Q_new.question_set.create(question_text="1. En desacuerdo, 2. Poco de acuerdo, 3. De acuerdo, 4. Totalmente de acuerdo", pub_date=timezone.now(),question_type="Label")

    lista_preguntas01 = [
        "1 El Centro nos informa satisfactoriamente de los progresos y dificultades de nuestros hijos",
        "2 El personal del Centro nos atiende cuando le planteamos cualquier asunto y se pueden expresar solicitudes, quejas y propuestas sobre el funcionamiento del Centro",
        "3 Hay una comunicación fácil entre familias y profesores o tutores",
        "4 Estamos satisfechos con las instalaciones del Centro y el mantenimiento de las mismas",
        "5 La agenda escolar es una buena forma de comunicación entre las familias y el Instituto",
        "6 En el Centro existe un clima escolar ordenado",
        "7 Además de la enseñanza habitual el Centro se ha preocupado por fomentar la formación en valores: respeto, solidaridad, etc.",
        "8 Estamos informados de los proyectos del Centro: de sus objetivos educativos, de los objetivos concretos que nuestros hijos han de alcanzar en cada asignatura o en la tutoría, de las asignaturas optativas que se pueden elegir, etc.",
        "9 Estamos satisfechos con los programas educativos que ofrece el Centro: Erasmus, 4º+Empresa, Compensatoria, Refuerzo escolar tardes, Campeonatos Escolares IPAFD, Teatro tardes, etc. También con la oferta de viajes y con las actividades extraescolares y complementarias que se llevan cabo",
        "10 Recibimos orientación sobre cómo deben estudiar nuestros hijos y sobre su futura vida profesional",
        "11 La documentación que el Centro utiliza para comunicarse con  nosotros es sencilla y práctica",
        "12 Las familias participamos en las actividades del Centro",
        "13 Estamos satisfechos con las actividades propuestas por el APA: actividades para alumnos y adultos por las tardes, charlas, etc."]

    for a in lista_preguntas01:
        q_new = Q_new.question_set.create(question_text=a, pub_date=timezone.now(),question_type="Choice4")
        for choice in ["1. En desacuerdo","2. Poco de acuerdo","3. De acuerdo", "4. Totalmente de acuerdo"]:
            q_new.choice_set.create(choice_text=choice,votes=0)
        
#    Q_new.question_set.create(question_text="CUESTIONES", pub_date=timezone.now(),question_type="Label")

    a="OPINIÓN GLOBAL SOBRE EL CENTRO (1.M 2.R 3.B 4.MB)"
    q_new = Q_new.question_set.create(question_text=a, pub_date=timezone.now(),question_type="Choice")
    for choice in ["1. MALO","2. REGULAR","3. BUENO","4. MUY BUENO"]:
        q_new.choice_set.create(choice_text=choice,votes=0)
    Q_new.question_set.create(question_text="OBSERVACIONES", pub_date=timezone.now(),question_type="Text")

def crear_encuestas_pas():
  g="pas"
  crear=True
  for q in Questionarie.objects.all():
    if q.questionarie_group==g:
      crear=False
      print("No creamos la encuesta para : "+q.questionarie_group)
  if crear:
    print("Creamos la encuesta para : "+g)

    Q_new=Questionarie(questionarie_text="Cuestionario para la evaluación del instituto", questionarie_group=g)
    Q_new.save()

#    Q_new.question_set.create(question_text="Cuestionario para la evaluación del instituto",pub_date=timezone.now(),question_type="Label")
    Q_new.question_set.create(question_text="1. En desacuerdo, 2. Poco de acuerdo, 3. De acuerdo, 4. Totalmente de acuerdo", pub_date=timezone.now(),question_type="Label")

    lista_preguntas01 = [
    	"1 La relación entre el personal no docente es productiva",
    	"2 La relación entre el personal no docente y el profesorado es productiva",
    	"3 La relación entre el personal no docente  y el alumnado es productiva",
    	"4 La relación entre el personal no docente y el Equipo Directivo es productiva",
    	"5 La relación entre el personal no docente y las familias es productiva",
    	"6 Los horarios han sido satisfactorios",
    	"7 El grado de satisfacción con el ambiente y el clima del Centro es alto",
    	"8 El Centro permite el desarrollo personal y profesional adecuados, dando oportunidades para aprender y mejorar",
    	"9 El grado de asunción de responsabilidades es adecuado",
    	"10 Existe reconocimiento de la labor desarrollada por parte de los miembros de la comunidad educativa",
    	"11 Se siente identificado con el Proyecto Educativo y los planes del Centro",
    	"12 Su trabajo es evaluado y de alguna manera se le ayuda a mejorarlo",
    	"13 El Equipo Directivo procura facilitar los recursos necesarios para hacer bien su trabajo",
    	"14 Recibe un trato justo y equitativo por la dirección del Centro",
    	"15 Siente que puede participar de las actividades del centro si lo desea"
	]

    for a in lista_preguntas01:
        q_new = Q_new.question_set.create(question_text=a, pub_date=timezone.now(),question_type="Choice4")
        for choice in ["1. En desacuerdo","2. Poco de acuerdo","3. De acuerdo", "4. Totalmente de acuerdo"]:
            q_new.choice_set.create(choice_text=choice,votes=0)
        
#    Q_new.question_set.create(question_text="CUESTIONES", pub_date=timezone.now(),question_type="Label")

    a="OPINIÓN GLOBAL SOBRE EL CENTRO (1.M 2.R 3.B 4.MB)"
    q_new = Q_new.question_set.create(question_text=a, pub_date=timezone.now(),question_type="Choice")
    for choice in ["1. MALO","2. REGULAR","3. BUENO","4. MUY BUENO"]:
        q_new.choice_set.create(choice_text=choice,votes=0)
    Q_new.question_set.create(question_text="OBSERVACIONES", pub_date=timezone.now(),question_type="Text")



    
def crear_encuestas(request):
  if request.user.is_authenticated:
    if request.user.is_superuser:
      print("Vamos a crear la encuestas de los alumnos")
      crear_encuestas_alumnos()
      print("Vamos a crear la encuestas de los profesores")
      crear_encuestas_docentes()
      print("Vamos a crear la encuestas de las familias")
      crear_encuestas_familia()
      print("Vamos a crear la encuestas del pas")
      crear_encuestas_pas()

      return render(request, "polls/welcome.html")
    else:
      return render(request, "polls/welcome.html")
  return redirect('/login')
 
