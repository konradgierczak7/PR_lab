using System;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Kopalnia
{
    class Program
    {
        const int RozmiarZloza = 2000;
        const int PojemnoscPojazdu = 200;
        const int CzasWydobycia = 10;
        const int CzasRozladunku = 10;
        const int CzasPrzejazdu = 10000;
        const int LiczbaGornikow = 5;

        static int zloze = RozmiarZloza;
        static int magazyn = 0;

        static SemaphoreSlim semZloze = new SemaphoreSlim(2, 2);
        static SemaphoreSlim semMagazyn = new SemaphoreSlim(1, 1);

        static object lockZloze = new object();
        static object lockMagazyn = new object();
        static object lockKonsola = new object();

        static string[] statusy = new string[LiczbaGornikow];
        static volatile bool koniec = false;

        static void Main(string[] args)
        {
            Console.OutputEncoding = Encoding.UTF8;
            ThreadPool.SetMinThreads(32, 32);
            Console.Clear();
            Console.CursorVisible = false;

            for (int i = 0; i < LiczbaGornikow; i++) statusy[i] = "Start";

            Task podglad = Task.Run(() => PetlaPodgladu());

            Task[] gornicy = new Task[LiczbaGornikow];
            for (int i = 0; i < gornicy.Length; i++)
            {
                int id = i + 1;
                gornicy[i] = Task.Run(() => Gornik(id));
            }
            Task.WaitAll(gornicy);

            koniec = true;
            podglad.Wait();

            Console.CursorVisible = true;
            Console.SetCursorPosition(0, LiczbaGornikow + 4);
            Console.WriteLine("Symulacja zakończona.");
        }

        static void Gornik(int id)
        {
            while (true)
            {
                UstawStatus(id, "Czeka na dostęp do złoża...");
                semZloze.Wait();
                UstawStatus(id, "Wydobywa węgiel...");
                int ladunek = 0;
                while (ladunek < PojemnoscPojazdu)
                {
                    lock (lockZloze )
                    {
                        if (zloze == 0) break;
                        zloze--;
                    }
                    Thread.Sleep(CzasWydobycia);
                    ladunek++;
                }
                semZloze.Release();

                if (ladunek == 0) break;

                UstawStatus(id, "Transportuje do magazynu...");
                Thread.Sleep(CzasPrzejazdu);

                UstawStatus(id, "Czeka na dostęp do magazynu...");
                semMagazyn.Wait();
                UstawStatus(id, "Rozładowuje węgiel...");
                for (int i = 0; i < ladunek; i++)
                {
                    Thread.Sleep(CzasRozladunku);
                    lock (lockMagazyn) magazyn++;
                }
                semMagazyn.Release();
            }
            UstawStatus(id, "Zakończył pracę.");
        }

        static void UstawStatus(int id, string s)
        {
            statusy[id - 1] = s;
        }

        static void PetlaPodgladu()
        {
            while (!koniec)
            {
                Wypisz();
                Thread.Sleep(100);
            }
            Wypisz();
        }

        static void Wypisz()
        {
            int z, m;
            lock (lockZloze) z = zloze;
            lock (lockMagazyn) m = magazyn;

            lock (lockKonsola)
            {
                Console.SetCursorPosition(0, 0);
                Console.WriteLine($"Stan złoża: {z} jednostek węgla".PadRight(50));
                Console.WriteLine($"Stan magazynu: {m} jednostek węgla".PadRight(50));
                Console.WriteLine();
                for (int i = 0; i < LiczbaGornikow; i++)
                    Console.WriteLine($"Górnik {i + 1}: {statusy[i]}".PadRight(50));
            }
        }
    }
}