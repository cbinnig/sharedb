"""Face identifier using the face_recognition library."""
import face_recognition


from .classifier import Classifier


class FaceClassifier(Classifier):
    def __init__(self):
        pass

    def rate(self, column):
        # Test to see if this is a column of file paths
        try:
            open(column[0])
        except OSError:
            return 0

        score = 0
        for row in column:
            try:
                image = face_recognition.load_image_file(row)
                face_locations = face_recognition.face_locations(image)
                if len(face_locations) > 0:
                    score += 1
            except OSError:
                continue
        return score / len(column)
