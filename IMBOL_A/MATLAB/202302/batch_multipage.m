explog=uiimport('-file');
explog=struct2table(explog);

home=uigetdir('/Users/bernardo/Bernardo_Local');
folders_f=dir([home,'/*front']);
folders_Ud=dir([home,'/*front_Ud']);
nfolders=length(folders_f);
H_setmm=explog{:,'H_mm'};
Pmbar=explog{:,'P_mbar'};
T_needleC=explog{:,'Tneedle_C'};
T_resC=explog{:,'Tres_C'};
T_surfC=explog{:,'Tsurf_C'};

for i=1:nfolders
    imfiles_f=getImfiles([folders_f(i).folder,'/',folders_f(i).name]);
    expnum=folders_f(i).name;
    expnum=expnum(1:15);
    loadim_multipage;
    impactspeed;
    spreading;
    D_b=D_f*0;
%     bottom_diameter;
    makeoutput(Hmm,Pmbar,T_needleC,T_resC,T_surfC,Dd,U,D_f,D_b,expnum,fps)
    system('python3 /Users/bernardo/Bernardo_Local/GIT/IMBOL/MATLAB/202212/appendresults')
    
end


clear('i','nfolders','test')





function files = getImfiles(folder)
imgs=dir([folder,'/*.tif']);
files=string(zeros(length(imgs),1));
for i= 1:length(imgs)
    test=startsWith(imgs(i).name,'.');
    if  ~test
    files(i)=[imgs(i).folder,'/',imgs(i).name];
    end
    
end
files=files(files~=string(0));

end

function makeoutput(Hmm,Pmbar,T_needleC,T_resC,T_surfC,Dd,U,D_f,D_b,expnum,fps)    
    
    t=0:length(D_b)-1;
    t=t'./fps;
    T = array2table([t,D_b,D_f]);
    T.Properties.VariableNames(1:width(T)) = {'t_s','Db_m','Df_m'}; 
    writetable(T,'Dvst/'+expnum+'_Dvst.csv','Delimiter',',');     
    Dmax_b=max(smooth(D_b));
    Dmax_f=max(smooth(D_f));
    T = cell2table({expnum,Hmm,Pmbar,T_needleC,T_resC,T_surfC,Dd,U,Dmax_b,Dmax_f});
    T.Properties.VariableNames(1:width(T)) = {'ExpNum','H_mm','P_mbar','Tneedle_C','Tres_C','Tsurf_C','Dd_m','U_m_s','Dmaxb_m','Dmaxf_m'};
    writetable(T,'Results_temp.csv','Delimiter',',');
    
    
    

end