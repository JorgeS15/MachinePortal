import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

import '../models/machine.dart';

class MachineRepository {
  static const _dbName = 'machineportal.db';
  static const _table = 'machines';

  final FlutterSecureStorage _secure = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );

  Database? _db;

  Future<Database> _open() async {
    if (_db != null) return _db!;
    final dbPath = join(await getDatabasesPath(), _dbName);
    _db = await openDatabase(
      dbPath,
      version: 1,
      onCreate: (db, _) => db.execute('''
        CREATE TABLE $_table (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          ip TEXT NOT NULL,
          ssh INTEGER NOT NULL DEFAULT 0,
          ssh_user TEXT NOT NULL DEFAULT 'user',
          ssh_port INTEGER NOT NULL DEFAULT 22,
          vnc_port INTEGER NOT NULL DEFAULT 5900
        )
      '''),
    );
    return _db!;
  }

  Future<List<Machine>> all() async {
    final db = await _open();
    final rows = await db.query(_table, orderBy: 'name COLLATE NOCASE');
    return rows.map(Machine.fromMap).toList();
  }

  Future<void> insert(Machine m, String password) async {
    final db = await _open();
    await db.insert(_table, m.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
    if (m.ssh && password.isNotEmpty) {
      await _secure.write(key: _pwKey(m.id), value: password);
    }
  }

  Future<void> update(Machine m, String? password) async {
    final db = await _open();
    await db.update(_table, m.toMap(), where: 'id = ?', whereArgs: [m.id]);
    if (password != null) {
      if (password.isEmpty) {
        await _secure.delete(key: _pwKey(m.id));
      } else {
        await _secure.write(key: _pwKey(m.id), value: password);
      }
    }
  }

  Future<void> delete(String id) async {
    final db = await _open();
    await db.delete(_table, where: 'id = ?', whereArgs: [id]);
    await _secure.delete(key: _pwKey(id));
  }

  Future<String> getPassword(String machineId) async {
    return await _secure.read(key: _pwKey(machineId)) ?? '';
  }

  String _pwKey(String id) => 'ssh_pw_$id';
}
