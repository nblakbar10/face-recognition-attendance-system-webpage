PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE karyawan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                nik TEXT NOT NULL,
                jenis_kelamin TEXT NOT NULL,
                jabatan TEXT NOT NULL,
                departemen TEXT NOT NULL
            );
INSERT INTO karyawan VALUES(1,'rahmadi','213123123123123','Pria','Staff','Engineering');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('karyawan',1);
COMMIT;
