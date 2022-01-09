for f in *.sh; do
	dos2unix $f
	chmod +rwx $f
done